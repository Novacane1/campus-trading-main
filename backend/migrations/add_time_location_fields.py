"""
添加时空约束字段
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # 为 items 表添加时空约束字段
    op.add_column('items', sa.Column('available_time_slots', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('items', sa.Column('preferred_locations', postgresql.ARRAY(sa.String()), nullable=True))

    # 为 users 表添加常用时间和地点字段
    op.add_column('users', sa.Column('usual_time_slots', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('users', sa.Column('usual_locations', postgresql.ARRAY(sa.String()), nullable=True))


def downgrade():
    op.drop_column('users', 'usual_locations')
    op.drop_column('users', 'usual_time_slots')
    op.drop_column('items', 'preferred_locations')
    op.drop_column('items', 'available_time_slots')
