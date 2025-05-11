#!/bin/bash

echo "===== 开始设置基于区块链信任机制的共享经济租赁平台 ====="

# 提示用户创建PostgreSQL数据库
echo "请确保已手动创建PostgreSQL数据库:"
echo "1. 使用psql命令行: CREATE DATABASE rental_platform;"
echo "2. 或使用pgAdmin等工具创建数据库"
echo ""
read -p "数据库是否已创建？(y/n): " db_created

if [ "$db_created" != "y" ]; then
    echo "请先创建数据库后再继续"
    exit 1
fi

# 创建迁移
echo "创建数据库迁移..."
python manage.py makemigrations blockchain_rental

# 应用迁移
echo "应用数据库迁移..."
python manage.py migrate

# 创建超级用户
echo "创建管理员账户..."
python manage.py createsuperuser

# 运行服务器
echo "启动开发服务器..."
python manage.py runserver

echo "===== 设置完成 =====" 