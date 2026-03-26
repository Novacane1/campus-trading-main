"""
测试配置文件
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试数据库配置
TEST_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/campus_trading_test'
TEST_REDIS_HOST = 'localhost'
TEST_REDIS_PORT = 6379
TEST_REDIS_DB = 1  # 使用不同的Redis数据库避免污染生产数据
