"""add_index_earnings_call_summary_created_at

Revision ID: c1d2e3f4a5b6
Revises: b0c1d2e3f4a5
Create Date: 2026-06-14 00:00:00.000000

"""
from alembic import op

revision = 'c1d2e3f4a5b6'
down_revision = 'b0c1d2e3f4a5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        'ix_earnings_call_summary_created_at',
        'earnings_call_summary',
        ['created_at'],
    )


def downgrade():
    op.drop_index('ix_earnings_call_summary_created_at', table_name='earnings_call_summary')
