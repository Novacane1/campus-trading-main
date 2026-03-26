"""
数据库迁移脚本：添加公告、举报、申诉、Banner表
运行方式: cd backend && python migrations/add_admin_features.py
"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def migrate():
    app = create_app()
    with app.app_context():
        # 创建新表
        db.create_all()
        print("数据库迁移完成：已创建 announcements, reports, appeals, banners 表")

if __name__ == '__main__':
    migrate()
