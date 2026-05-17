"""create_ai_prompt

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c4d5e6f7a8b9'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ai_prompt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(50), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'provider', name='uix_ai_prompt_name_provider'),
    )
    op.create_index('ix_ai_prompt_name', 'ai_prompt', ['name'])
    op.create_index('ix_ai_prompt_provider', 'ai_prompt', ['provider'])


def downgrade():
    op.drop_index('ix_ai_prompt_provider', 'ai_prompt')
    op.drop_index('ix_ai_prompt_name', 'ai_prompt')
    op.drop_table('ai_prompt')
