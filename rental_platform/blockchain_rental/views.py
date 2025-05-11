from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt # 生产环境中请谨慎使用或正确配置CSRF
import json
from web3 import Web3 # 需要导入 Web3 用于 is_address 校验
from django.conf import settings

from .blockchain_interface import BlockchainInterface # 导入我们更新后的接口

# Create your views here.

# --- 区块链浏览器视图 ---

def explorer_view(request):
    """
    区块链浏览器页面视图，用于展示合约交互历史。
    """
    context = {
        'contract_address': settings.RENTAL_PLATFORM_CONTRACT_ADDRESS
    }
    return render(request, 'blockchain_rental/explorer.html', context)


# --- 视图：准备交易数据 (供前端签名) ---

@csrf_exempt # 注意CSRF处理
@require_http_methods(["POST"]) # 只接受POST请求
def prepare_user_registration_tx(request):
    """
    准备用户注册的交易数据。
    前端应发送包含 'name', 'email', 和可选的 'fromAddress' 的JSON体。
    """
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        # from_address 用于估算 gas, 前端钱包实际发送时会使用自己的地址
        from_address_for_gas = data.get('fromAddress') 
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '无效的JSON请求体。'}, status=400)

    if not name or not email:
        return JsonResponse({'status': 'error', 'message': '必须提供姓名和邮箱。'}, status=400)

    if not BlockchainInterface.is_ready():
        return JsonResponse({
            'status': 'error', 
            'message': BlockchainInterface.get_error_message() or "区块链接口未初始化。"
        }, status=503) # 503 Service Unavailable

    # 调用旧接口名称的方法，它现在内部准备交易数据
    blockchain_response = BlockchainInterface.verify_identity(
        {'name': name, 'email': email}, 
        from_address=from_address_for_gas
    )

    if blockchain_response.get('error'):
        return JsonResponse({
            'status': 'error', 
            'message': f"准备交易失败: {blockchain_response['error']}"
        }, status=400)
    
    if not blockchain_response.get('tx_data'):
        return JsonResponse({
            'status': 'error', 
            'message': "准备交易失败: 未返回交易数据。"
        }, status=500) # Internal Server Error

    return JsonResponse({
        'status': 'success',
        'message': '用户注册交易数据准备成功。请使用钱包签名并发送。',
        'transaction_params': blockchain_response['tx_data']
    })


@csrf_exempt
@require_http_methods(["POST"])
def prepare_property_registration_tx(request):
    """
    准备房源注册的交易数据。
    前端应发送包含 'title', 'description', 'price', 和可选 'fromAddress' 的JSON体。
    """
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        price_str = data.get('price') # 价格通常作为字符串或数字接收
        from_address_for_gas = data.get('fromAddress')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '无效的JSON请求体。'}, status=400)

    if not all([title, description, price_str is not None]):
        return JsonResponse({'status': 'error', 'message': '必须提供标题、描述和价格。'}, status=400)
    
    try:
        price = int(price_str) # 合约需要 uint256
    except ValueError:
        return JsonResponse({'status': 'error', 'message': '价格必须是有效的整数。'}, status=400)

    if not BlockchainInterface.is_ready():
        return JsonResponse({'status': 'error', 'message': BlockchainInterface.get_error_message() or "区块链接口未初始化。"}, status=503)

    blockchain_response = BlockchainInterface.register_property(
        {'title': title, 'description': description, 'price': price},
        from_address=from_address_for_gas
    )

    if blockchain_response.get('error'):
        return JsonResponse({'status': 'error', 'message': f"准备交易失败: {blockchain_response['error']}"}, status=400)
    if not blockchain_response.get('tx_data'):
        return JsonResponse({'status': 'error', 'message': "准备交易失败: 未返回交易数据。"}, status=500)

    return JsonResponse({
        'status': 'success',
        'message': '房源注册交易数据准备成功。请使用钱包签名并发送。',
        'transaction_params': blockchain_response['tx_data']
    })

# 您可以为 create_booking, confirm_booking, complete_booking, submit_review 添加类似的准备交易视图
# 例如:
# @csrf_exempt
# @require_http_methods(["POST"])
# def prepare_create_booking_tx_view(request):
#     # ... (实现逻辑，从 request.body 获取 property_id, start_date, end_date, value_in_wei (可选))
#     # ... (调用 BlockchainInterface.create_booking_contract 或 prepare_create_booking_tx)
#     # ... (返回 transaction_params)
#     pass


# --- 视图：读取链上数据 ---

@require_http_methods(["GET"])
def get_user_blockchain_info(request, user_address: str):
    """
    从区块链获取特定用户的信息。
    user_address 应作为URL路径参数传递。
    """
    if not BlockchainInterface.is_ready():
        return JsonResponse({'status': 'error', 'message': BlockchainInterface.get_error_message() or "区块链接口未初始化。"}, status=503)

    # 可选：验证 user_address 是否是有效的以太坊地址格式
    if not Web3.is_address(user_address): 
         return JsonResponse({'status': 'error', 'message': '无效的用户地址格式。'}, status=400)

    user_info = BlockchainInterface.get_user_info(user_address)

    if user_info.get('error'):
        # 如果错误是由于用户不存在（例如，call revert），这可能是预期的
        # 您可能需要根据错误类型返回不同的状态码或消息
        return JsonResponse({'status': 'error', 'message': user_info['error']}, status=404) 
    
    return JsonResponse({'status': 'success', 'data': user_info})


@require_http_methods(["GET"])
def get_property_blockchain_info(request, property_id: int):
    """
    从区块链获取特定房源的信息。
    property_id 应作为URL路径参数传递，并确保它是整数。
    """
    if not BlockchainInterface.is_ready():
        return JsonResponse({'status': 'error', 'message': BlockchainInterface.get_error_message() or "区块链接口未初始化。"}, status=503)
    
    try:
        # 确保 property_id (从URL捕获) 确实是整数，尽管Django URL转换器通常会处理
        prop_id_int = int(property_id) 
    except ValueError:
        return JsonResponse({'status': 'error', 'message': '房源ID必须是整数。'}, status=400)

    property_info = BlockchainInterface.get_property_info(prop_id_int)

    if property_info.get('error'):
        return JsonResponse({'status': 'error', 'message': property_info['error']}, status=404)
        
    return JsonResponse({'status': 'success', 'data': property_info})


@require_http_methods(["GET"])
def get_total_property_count(request):
    """
    从区块链获取已注册的房源总数。
    """
    if not BlockchainInterface.is_ready():
        return JsonResponse({'status': 'error', 'message': BlockchainInterface.get_error_message() or "区块链接口未初始化。"}, status=503)

    count_info = BlockchainInterface.get_property_count()

    if count_info.get('error'):
        return JsonResponse({'status': 'error', 'message': count_info['error']}, status=500)
        
    return JsonResponse({'status': 'success', 'data': {'property_count': count_info.get('count')}})
