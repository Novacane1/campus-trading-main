"""
为 reviews 表添加 parent_id 字段以支持评价回复功能
同时将 order_id, reviewed_user_id, rating, review_type 设为 nullable
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:123456@localhost:5432/campus_trading')


def upgrade():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        # 添加 parent_id 列
        cur.execute("""
            ALTER TABLE reviews
            ADD COLUMN IF NOT EXISTS parent_id INTEGER REFERENCES reviews(id);
        """)

        # 将 order_id 改为 nullable（回复不需要关联订单）
        cur.execute("""
            ALTER TABLE reviews
            ALTER COLUMN order_id DROP NOT NULL;
        """)

        # 将 reviewed_user_id 改为 nullable（回复不需要被评价人）
        cur.execute("""
            ALTER TABLE reviews
            ALTER COLUMN reviewed_user_id DROP NOT NULL;
        """)

        # 将 rating 改为 nullable（回复不需要评分）
        cur.execute("""
            ALTER TABLE reviews
            ALTER COLUMN rating DROP NOT NULL;
        """)

        # 将 review_type 改为 nullable（回复使用 'reply' 类型）
        cur.execute("""
            ALTER TABLE reviews
            ALTER COLUMN review_type DROP NOT NULL;
        """)

        conn.commit()
        print("Migration completed: parent_id column added to reviews table.")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def downgrade():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        # 先删除所有回复
        cur.execute("DELETE FROM reviews WHERE parent_id IS NOT NULL;")
        # 移除 parent_id 列
        cur.execute("ALTER TABLE reviews DROP COLUMN IF EXISTS parent_id;")
        # 恢复 NOT NULL 约束
        cur.execute("ALTER TABLE reviews ALTER COLUMN order_id SET NOT NULL;")
        cur.execute("ALTER TABLE reviews ALTER COLUMN reviewed_user_id SET NOT NULL;")
        cur.execute("ALTER TABLE reviews ALTER COLUMN rating SET NOT NULL;")
        cur.execute("ALTER TABLE reviews ALTER COLUMN review_type SET NOT NULL;")
        conn.commit()
        print("Downgrade completed: parent_id column removed from reviews table.")
    except Exception as e:
        conn.rollback()
        print(f"Downgrade failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    upgrade()
