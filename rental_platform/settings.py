# Blockchain Configuration
SEPOLIA_RPC_URL = 'https://eth-sepolia.g.alchemy.com/v2/9LXOdanO569UkCCU0ZvCh-4aQsdibYpE' # 这是您的 RPC URL
RENTAL_PLATFORM_CONTRACT_ADDRESS = '0x179ca0718d26B693dC58245FcecFd1d70a22ad90' # 这是您的合约地址

# 合约 ABI
# 请将下面的 None 替换为从 Hardhat artifact JSON 文件中 "abi" 键复制的 Python 列表,
# 或者一个包含 ABI 的 JSON 字符串。
# 示例 1 (Python 列表): RENTAL_PLATFORM_CONTRACT_ABI = [{'inputs': [], 'name': 'foo', ...}]
# 示例 2 (JSON 字符串): RENTAL_PLATFORM_CONTRACT_ABI = '[{"inputs": [], "name": "foo", ...}]'
RENTAL_PLATFORM_CONTRACT_ABI = [
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "bookingId",
          "type": "uint256"
        }
      ],
      "name": "BookingCompleted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "bookingId",
          "type": "uint256"
        }
      ],
      "name": "BookingConfirmed",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "bookingId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "tenant",
          "type": "address"
        }
      ],
      "name": "BookingCreated",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "string",
          "name": "title",
          "type": "string"
        }
      ],
      "name": "PropertyRegistered",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "reviewer",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "rating",
          "type": "uint256"
        }
      ],
      "name": "ReviewSubmitted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "UserRegistered",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "bookingCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "bookings",
      "outputs": [
        {
          "internalType": "address",
          "name": "tenant",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "startDate",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "endDate",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "totalPrice",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "isConfirmed",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "isCompleted",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_bookingId",
          "type": "uint256"
        }
      ],
      "name": "completeBooking",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_bookingId",
          "type": "uint256"
        }
      ],
      "name": "confirmBooking",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_propertyId",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "_startDate",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "_endDate",
          "type": "uint256"
        }
      ],
      "name": "createBooking",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_bookingId",
          "type": "uint256"
        }
      ],
      "name": "getBookingInfo",
      "outputs": [
        {
          "components": [
            {
              "internalType": "address",
              "name": "tenant",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "propertyId",
              "type": "uint256"
            },
            {
              "internalType": "uint256",
              "name": "startDate",
              "type": "uint256"
            },
            {
              "internalType": "uint256",
              "name": "endDate",
              "type": "uint256"
            },
            {
              "internalType": "uint256",
              "name": "totalPrice",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "isConfirmed",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "isCompleted",
              "type": "bool"
            }
          ],
          "internalType": "struct RentalPlatform.Booking",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_propertyId",
          "type": "uint256"
        }
      ],
      "name": "getPropertyInfo",
      "outputs": [
        {
          "components": [
            {
              "internalType": "address",
              "name": "owner",
              "type": "address"
            },
            {
              "internalType": "string",
              "name": "title",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "description",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "price",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "isAvailable",
              "type": "bool"
            },
            {
              "internalType": "uint256[]",
              "name": "bookingIds",
              "type": "uint256[]"
            },
            {
              "internalType": "uint256",
              "name": "reputation",
              "type": "uint256"
            }
          ],
          "internalType": "struct RentalPlatform.Property",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_propertyId",
          "type": "uint256"
        }
      ],
      "name": "getPropertyReviews",
      "outputs": [
        {
          "components": [
            {
              "internalType": "address",
              "name": "reviewer",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "propertyId",
              "type": "uint256"
            },
            {
              "internalType": "uint256",
              "name": "rating",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "comment",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            }
          ],
          "internalType": "struct RentalPlatform.Review[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_user",
          "type": "address"
        }
      ],
      "name": "getUserInfo",
      "outputs": [
        {
          "components": [
            {
              "internalType": "string",
              "name": "name",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "email",
              "type": "string"
            },
            {
              "internalType": "bool",
              "name": "isVerified",
              "type": "bool"
            },
            {
              "internalType": "uint256",
              "name": "reputation",
              "type": "uint256"
            },
            {
              "internalType": "uint256",
              "name": "joinDate",
              "type": "uint256"
            }
          ],
          "internalType": "struct RentalPlatform.User",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "properties",
      "outputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "title",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "description",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "price",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "isAvailable",
          "type": "bool"
        },
        {
          "internalType": "uint256",
          "name": "reputation",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "propertyCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "propertyReviews",
      "outputs": [
        {
          "internalType": "address",
          "name": "reviewer",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "propertyId",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "rating",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "comment",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_title",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_description",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_price",
          "type": "uint256"
        }
      ],
      "name": "registerProperty",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_email",
          "type": "string"
        }
      ],
      "name": "registerUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_propertyId",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "_rating",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "_comment",
          "type": "string"
        }
      ],
      "name": "submitReview",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "users",
      "outputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "email",
          "type": "string"
        },
        {
          "internalType": "bool",
          "name": "isVerified",
          "type": "bool"
        },
        {
          "internalType": "uint256",
          "name": "reputation",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "joinDate",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
  ]  # <--- 重要：请将这里替换为您的真实 ABI (Python列表或JSON字符串)

# 可选：后端签名账户
# BACKEND_SIGNER_PRIVATE_KEY = 'YOUR_BACKEND_WALLET_PRIVATE_KEY' # 存储私钥有风险，请谨慎使用
# BACKEND_SIGNER_ADDRESS = 'YOUR_BACKEND_WALLET_ADDRESS'

import json

if RENTAL_PLATFORM_CONTRACT_ABI is None:
    print("警告: RENTAL_PLATFORM_CONTRACT_ABI 未在 settings.py 中配置。")
    # 在后续代码中，您可能需要检查 ABI 是否已正确加载，或者提供一个默认的空列表
    # RENTAL_PLATFORM_CONTRACT_ABI = [] 
elif isinstance(RENTAL_PLATFORM_CONTRACT_ABI, str):
    try:
        RENTAL_PLATFORM_CONTRACT_ABI = json.loads(RENTAL_PLATFORM_CONTRACT_ABI)
    except json.JSONDecodeError:
        print(f"警告: RENTAL_PLATFORM_CONTRACT_ABI 字符串无法被解析为 JSON。请确保它是有效的 JSON 格式。ABI: {RENTAL_PLATFORM_CONTRACT_ABI[:200]}...") # 打印前200个字符以帮助调试
        # RENTAL_PLATFORM_CONTRACT_ABI = [] # 或者抛出配置错误
    except Exception as e:
        print(f"处理 ABI 字符串时发生未知错误: {e}")
        # RENTAL_PLATFORM_CONTRACT_ABI = []
# 如果 RENTAL_PLATFORM_CONTRACT_ABI 直接就是一个列表 (推荐方式)，则不需要额外处理。

# 校验 ABI 是否最终成为一个列表
if not isinstance(RENTAL_PLATFORM_CONTRACT_ABI, list):
    print("错误: RENTAL_PLATFORM_CONTRACT_ABI 未能成功加载为列表。请检查 settings.py 中的配置。")
    # 对于关键配置，您可能希望在这里引发一个 ImproperlyConfigured 异常
    # from django.core.exceptions import ImproperlyConfigured
    # raise ImproperlyConfigured("RENTAL_PLATFORM_CONTRACT_ABI 未能成功加载。")
    RENTAL_PLATFORM_CONTRACT_ABI = [] # 暂时设置为默认空列表以避免运行时错误，但应修复配置 