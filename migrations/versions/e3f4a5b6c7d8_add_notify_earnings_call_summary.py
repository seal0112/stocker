"""add notify_earnings_call_summary to push_notification

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-06-14

"""
from alembic import op
import sqlalchemy as sa

revision = 'e3f4a5b6c7d8'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('push_notification',
        sa.Column('notify_earnings_call_summary', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade():
    op.drop_column('push_notification', 'notify_earnings_call_summary')
