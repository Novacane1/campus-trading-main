"""
添加风控系统表
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # 创建风控日志表
    op.create_table('risk_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=32), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('device_id', sa.String(length=128), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_logs_created_at'), 'risk_logs', ['created_at'], unique=False)

    # 创建用户风险标签表
    op.create_table('user_risk_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tag_type', sa.String(length=32), nullable=False),
        sa.Column('severity', sa.String(length=16), nullable=True),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('auto_tagged', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_risk_tags_user_id'), 'user_risk_tags', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_user_risk_tags_user_id'), table_name='user_risk_tags')
    op.drop_table('user_risk_tags')
    op.drop_index(op.f('ix_risk_logs_created_at'), table_name='risk_logs')
    op.drop_table('risk_logs')
