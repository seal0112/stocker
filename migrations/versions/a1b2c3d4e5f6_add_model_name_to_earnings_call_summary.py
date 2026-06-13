"""add_model_name_to_earnings_call_summary

Revision ID: a1b2c3d4e5f6
Revises: e6f7a8b9c0d1
Create Date: 2026-06-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'e6f7a8b9c0d1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('earnings_call_summary',
        sa.Column('model_name', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('earnings_call_summary', 'model_name')
