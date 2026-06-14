"""create_ai_api_key_and_update_ai_prompt

Revision ID: b0c1d2e3f4a5
Revises: f8a9b0c1d2e3
Create Date: 2026-06-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b0c1d2e3f4a5'
down_revision = 'f8a9b0c1d2e3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ai_api_key',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('owner', sa.String(100), nullable=True),
        sa.Column('ssm_path', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uix_ai_api_key_name'),
        sa.UniqueConstraint('ssm_path', name='uix_ai_api_key_ssm_path'),
    )

    op.add_column('ai_prompt',
        sa.Column('api_key_id', sa.Integer(), sa.ForeignKey('ai_api_key.id'), nullable=True))


def downgrade():
    op.drop_column('ai_prompt', 'api_key_id')
    op.drop_table('ai_api_key')
