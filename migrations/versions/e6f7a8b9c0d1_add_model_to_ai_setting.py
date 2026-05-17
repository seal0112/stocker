"""add_model_to_ai_setting

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'e6f7a8b9c0d1'
down_revision = 'd5e6f7a8b9c0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ai_setting',
        sa.Column('model', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('ai_setting', 'model')
