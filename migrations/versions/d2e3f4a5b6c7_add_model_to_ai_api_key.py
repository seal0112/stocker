"""add model to ai_api_key

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-06-14

"""
from alembic import op
import sqlalchemy as sa

revision = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ai_api_key', sa.Column('model', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('ai_api_key', 'model')
