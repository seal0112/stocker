"""create_ai_setting

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd5e6f7a8b9c0'
down_revision = 'c4d5e6f7a8b9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ai_setting',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('provider', sa.String(50), nullable=False, server_default='gemini'),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    # Insert default row
    op.execute("INSERT INTO ai_setting (provider, updated_by) VALUES ('gemini', 'system')")


def downgrade():
    op.drop_table('ai_setting')
