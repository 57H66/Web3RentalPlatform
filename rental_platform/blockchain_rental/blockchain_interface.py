from web3 import Web3, HTTPProvider
# from web3.providers.http import HTTPProvider
# from web3.middleware import geth_poa_middleware # 如果连接到 PoA 网络如 Sepolia, 可能需要
from django.conf import settings
# from hexbytes import HexBytes # HexBytes 可能不再直接需要，除非处理返回的字节数据
import logging

logger = logging.getLogger(__name__)

class BlockchainInterface:
    """
    区块链接口 - 处理与区块链的所有交互。
    连接到在 settings.py 中配置的智能合约。
    此版本适配"用户前端钱包签名"模式：后端准备交易数据，前端签名并发送。
    """
    w3 = None
    contract = None
    initialized = False
    error_message = None 

    DUMMY_FROM_ADDRESS_FOR_GAS_ESTIMATION = '0x0000000000000000000000000000000000000001' # 用于估算gas的虚拟地址

    @classmethod
    def _initialize_web3(cls):
        if cls.initialized and cls.w3 and cls.contract:
            return True
        cls.error_message = None
        try:
            if not settings.SEPOLIA_RPC_URL:
                cls.error_message = "SEPOLIA_RPC_URL 未在 settings.py 中配置。"
                logger.error(cls.error_message)
                cls.initialized = False
                return False
            cls.w3 = Web3(HTTPProvider(settings.SEPOLIA_RPC_URL))
            # 对于 POA 网络, 如 Sepolia, 如果遇到连接或 'extraData' 错误, 可能需要以下中间件:
            # from web3.middleware import geth_poa_middleware
            # cls.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            if not cls.w3.is_connected():
                cls.error_message = f"无法连接到区块链节点: {settings.SEPOLIA_RPC_URL}"
                logger.error(cls.error_message)
                cls.initialized = False
                return False
            if not settings.RENTAL_PLATFORM_CONTRACT_ADDRESS or not settings.RENTAL_PLATFORM_CONTRACT_ABI:
                cls.error_message = "合约地址或 ABI 未在 settings.py 中正确配置。"
                logger.error(cls.error_message)
                cls.initialized = False
                return False
            try:
                contract_address = cls.w3.to_checksum_address(settings.RENTAL_PLATFORM_CONTRACT_ADDRESS)
            except ValueError as e:
                cls.error_message = f"提供的合约地址无效: {settings.RENTAL_PLATFORM_CONTRACT_ADDRESS} - {e}"
                logger.error(cls.error_message)
                cls.initialized = False
                return False
            cls.contract = cls.w3.eth.contract(
                address=contract_address,
                abi=settings.RENTAL_PLATFORM_CONTRACT_ABI
            )
            cls.initialized = True
            logger.info("区块链接口初始化成功。")
            return True
        except Exception as e:
            cls.error_message = f"区块链接口初始化失败: {e}"
            logger.exception(cls.error_message)
            cls.initialized = False
            return False

    @classmethod
    def get_error_message(cls):
        return cls.error_message

    @classmethod
    def is_ready(cls):
        if not cls.initialized:
            cls._initialize_web3()
        return cls.initialized and cls.w3 is not None and cls.contract is not None

    # --- 合约读取方法 (保持不变) ---
    @classmethod
    def get_user_info(cls, user_address: str) -> dict:
        if not cls.is_ready():
            return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        try:
            checksum_user_address = cls.w3.to_checksum_address(user_address)
            user_data_tuple = cls.contract.functions.getUserInfo(checksum_user_address).call()
            return {
                "name": user_data_tuple[0],
                "email": user_data_tuple[1],
                "isVerified": user_data_tuple[2],
                "reputation": user_data_tuple[3],
                "joinDate": user_data_tuple[4],
                "error": None
            }
        except Exception as e:
            logger.error(f"获取用户信息失败 ({user_address}): {e}")
            return {"error": str(e)}

    @classmethod
    def get_property_info(cls, property_id: int) -> dict:
        if not cls.is_ready():
            return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        try:
            prop_data_tuple = cls.contract.functions.getPropertyInfo(property_id).call()
            return {
                "owner": prop_data_tuple[0],
                "title": prop_data_tuple[1],
                "description": prop_data_tuple[2],
                "price": prop_data_tuple[3],
                "isAvailable": prop_data_tuple[4],
                "bookingIds": prop_data_tuple[5],
                "reputation": prop_data_tuple[6],
                "error": None
            }
        except Exception as e:
            logger.error(f"获取房源信息失败 (ID: {property_id}): {e}")
            return {"error": str(e)}
            
    @classmethod
    def get_property_count(cls) -> dict:
        if not cls.is_ready():
            return {"error": cls.get_error_message() or "区块链接口未初始化。", "count": None}
        try:
            count = cls.contract.functions.propertyCount().call()
            return {"count": count, "error": None}
        except Exception as e:
            logger.error(f"获取房源总数失败: {e}")
            return {"error": str(e), "count": None}

    # --- 交易数据准备方法 (用于前端签名和发送) ---
    @classmethod
    def _prepare_transaction_data(cls, contract_function_call, from_address_for_gas_estimation=None, value_in_wei=0) -> dict:
        """ (辅助方法) 准备调用合约函数所需的交易数据 """
        if not cls.is_ready():
            return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        
        from_addr = cls.w3.to_checksum_address(from_address_for_gas_estimation or cls.DUMMY_FROM_ADDRESS_FOR_GAS_ESTIMATION)

        try:
            # 准备基础交易参数以估算 gas
            tx_params_for_gas = {
                'from': from_addr,
                # 'to': cls.contract.address, # build_transaction 会自动填充 to
            }
            if value_in_wei > 0:
                tx_params_for_gas['value'] = value_in_wei

            estimated_gas = contract_function_call.estimate_gas(tx_params_for_gas)
            
            # 构建交易数据 (不包含 nonce, gasPrice, from - 这些由前端钱包处理)
            # 我们主要提供 to 和 data, 以及 value 和 estimated_gas 作为建议
            transaction_data = {
                'to': cls.contract.address,
                'data': contract_function_call.build_transaction(tx_params_for_gas)['data'], # 只取data字段
                'estimated_gas': estimated_gas,
                'value': value_in_wei, # 如果函数是 payable
                'error': None
            }
            return transaction_data
        except Exception as e:
            logger.error(f"准备交易数据失败 for {contract_function_call.fn_name}: {e}")
            # 尝试获取更具体的错误信息，例如合约 revert 原因
            error_reason = str(e)
            if hasattr(e, 'message') and e.message:
                 if isinstance(e.message, str) and "revert" in e.message.lower():
                    try:
                        # 尝试从错误消息中提取 revert 原因（这部分可能需要根据具体错误格式调整）
                        # 示例: "execution reverted: User already registered"
                        reason_start = e.message.lower().find("revert")
                        if reason_start != -1:
                            error_reason = e.message[reason_start + len("revert"):].strip()
                            if error_reason.startswith(":"):
                                error_reason = error_reason[1:].strip()
                    except Exception as parse_err:
                        logger.debug(f"解析 revert 原因失败: {parse_err}")
            return {"error": f"准备交易时出错: {error_reason}"}

    @classmethod
    def prepare_register_user_tx(cls, name: str, email: str, from_address: str = None) -> dict:
        """准备注册用户的交易数据"""
        if not cls.is_ready(): return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        if not name or not email:
            return {"error": "用户名和邮箱不能为空。"}
        contract_function = cls.contract.functions.registerUser(name, email)
        return cls._prepare_transaction_data(contract_function, from_address_for_gas_estimation=from_address)

    @classmethod
    def prepare_register_property_tx(cls, title: str, description: str, price: int, from_address: str = None) -> dict:
        """准备注册房源的交易数据"""
        if not cls.is_ready(): return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        if not all([title, description, price is not None]):
            return {"error": "房源标题、描述和价格不能为空。"}
        try:
            price = int(price)
        except ValueError:
            return {"error": "价格必须是有效的数字。"}
        contract_function = cls.contract.functions.registerProperty(title, description, price)
        return cls._prepare_transaction_data(contract_function, from_address_for_gas_estimation=from_address)

    @classmethod
    def prepare_create_booking_tx(cls, property_id: int, start_date: int, end_date: int, from_address: str = None, value_in_wei: int = 0) -> dict:
        """准备创建预订的交易数据"""
        if not cls.is_ready(): return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        if not all([property_id is not None, start_date is not None, end_date is not None]):
            return {"error": "property_id, start_date, 和 end_date 不能为空。"}
        try:
            property_id = int(property_id)
            start_date = int(start_date)
            end_date = int(end_date)
        except ValueError:
            return {"error": "property_id, start_date, end_date 必须是有效数字。"}
        
        # 假设 createBooking 合约函数不需要 msg.value (ETH支付)
        # 如果需要，前端在发送交易时应包含 value
        # 后端可以在这里也包含 value_in_wei (如果已知)
        contract_function = cls.contract.functions.createBooking(property_id, start_date, end_date)
        return cls._prepare_transaction_data(contract_function, from_address_for_gas_estimation=from_address, value_in_wei=value_in_wei)

    @classmethod
    def prepare_confirm_booking_tx(cls, booking_id: int, from_address: str = None) -> dict:
        """准备确认预订的交易数据"""
        if not cls.is_ready(): return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        try:
            booking_id = int(booking_id)
        except ValueError:
            return {"error": "booking_id 必须是有效数字。"}
        contract_function = cls.contract.functions.confirmBooking(booking_id)
        return cls._prepare_transaction_data(contract_function, from_address_for_gas_estimation=from_address)

    @classmethod
    def prepare_complete_booking_tx(cls, booking_id: int, from_address: str = None) -> dict:
        """准备完成预订的交易数据"""
        if not cls.is_ready(): return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        try:
            booking_id = int(booking_id)
        except ValueError:
            return {"error": "booking_id 必须是有效数字。"}
        contract_function = cls.contract.functions.completeBooking(booking_id)
        return cls._prepare_transaction_data(contract_function, from_address_for_gas_estimation=from_address)

    @classmethod
    def prepare_submit_review_tx(cls, property_id: int, rating: int, comment: str, from_address: str = None) -> dict:
        """准备提交评价的交易数据"""
        if not cls.is_ready(): return {"error": cls.get_error_message() or "区块链接口未初始化。"}
        if not all([property_id is not None, rating is not None]):
            return {"error": "property_id 和 rating 不能为空。"}
        try:
            property_id = int(property_id)
            rating = int(rating)
            if not (1 <= rating <= 5):
                 return {"error": "评级必须在1到5之间。"}
        except ValueError:
            return {"error": "property_id 和 rating 必须是有效数字。"}
        contract_function = cls.contract.functions.submitReview(property_id, rating, comment)
        return cls._prepare_transaction_data(contract_function, from_address_for_gas_estimation=from_address)

    # --- 映射旧的接口方法到新的准备方法 (如果Django视图还在使用旧名称) ---
    # 这些方法现在只准备交易数据，实际交易由前端处理。
    # 返回值结构也已改变。

    @classmethod
    def verify_identity(cls, user_data: dict, from_address: str = None) -> dict:
        """准备用户注册的交易数据。原 verify_identity。"""
        name = user_data.get('name')
        email = user_data.get('email')
        prepared_data = cls.prepare_register_user_tx(name, email, from_address)
        if prepared_data.get("error"):
            return {"error": prepared_data["error"], "tx_data": None}
        return {"error": None, "tx_data": prepared_data}

    @classmethod
    def register_property(cls, property_data: dict, from_address: str = None) -> dict:
        """准备房源注册的交易数据。原 register_property。"""
        title = property_data.get('title')
        description = property_data.get('description')
        price = property_data.get('price')
        prepared_data = cls.prepare_register_property_tx(title, description, price, from_address)
        if prepared_data.get("error"):
            return {"error": prepared_data["error"], "tx_data": None}
        return {"error": None, "tx_data": prepared_data}

    @classmethod
    def create_booking_contract(cls, booking_data: dict, from_address: str = None) -> dict:
        """准备创建预订的交易数据。原 create_booking_contract。"""
        property_id = booking_data.get('property_id')
        start_date = booking_data.get('start_date')
        end_date = booking_data.get('end_date')
        # value_in_wei = booking_data.get('value_in_wei', 0) # 如果前端传来支付金额
        prepared_data = cls.prepare_create_booking_tx(property_id, start_date, end_date, from_address)
        if prepared_data.get("error"):
            return {"error": prepared_data["error"], "tx_data": None}
        return {"error": None, "tx_data": prepared_data}

    @classmethod
    def verify_review(cls, review_data: dict, from_address: str = None) -> dict:
        """准备提交评价的交易数据。原 verify_review。"""
        property_id = review_data.get('property_id')
        rating = review_data.get('rating')
        comment = review_data.get('comment', '')
        prepared_data = cls.prepare_submit_review_tx(property_id, rating, comment, from_address)
        if prepared_data.get("error"):
            return {"error": prepared_data["error"], "tx_data": None}
        return {"error": None, "tx_data": prepared_data}

# 可以在 Django 应用加载时尝试初始化，以便尽早发现配置问题。
# BlockchainInterface._initialize_web3() 