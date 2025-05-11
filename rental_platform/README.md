# 基于区块链信任机制的共享经济租赁平台

这是一个基于Django和PostgreSQL开发的共享经济租赁平台最小可行产品(MVP)，核心特点是利用区块链技术建立和增强房东与租客之间的信任关系。

## 项目特点

- **区块链身份验证**：用户可以通过区块链验证其身份，提高平台信任度
- **房源链上验证**：房源信息可以存储哈希值到区块链，保证真实性
- **智能合约预订**：预订信息通过区块链智能合约记录，确保条款不可篡改
- **链上评价验证**：用户评价通过区块链验证，提高可信度

## 技术栈

- **后端框架**：Django 4.2.10
- **数据库**：PostgreSQL
- **区块链接口**：自定义模拟接口（可替换为实际区块链实现）
- **API**：Django REST Framework

## 核心模型结构

1. **User**：用户模型，包含区块链地址与身份验证信息
2. **Property**：房源模型，包含基本信息和区块链验证字段
3. **Booking**：预订模型，关联智能合约信息
4. **Review**：评价模型，包含链上验证机制
5. **BlockchainTransaction**：记录所有区块链交易

## 快速开始

### 环境准备

确保已安装Python 3.8+和PostgreSQL。

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置数据库

1. 创建PostgreSQL数据库
2. 更新`config/settings.py`中的数据库配置

### 初始化数据库

```bash
python manage.py migrate
```

### 创建管理员账户

```bash
python manage.py createsuperuser
```

### 运行服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/admin/ 登录管理员界面。

## 区块链集成

当前版本使用模拟的区块链接口，您可以根据需要替换为实际的区块链实现（如以太坊、Solana等）。核心接口位于`blockchain_rental/blockchain_interface.py`。

## 安全注意事项

- 实际部署时请更新`SECRET_KEY`
- 为敏感配置使用环境变量
- 实现适当的权限控制 