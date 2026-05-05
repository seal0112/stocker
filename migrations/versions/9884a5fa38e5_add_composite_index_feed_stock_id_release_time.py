"""add composite index feed stock_id releaseTime

Revision ID: 9884a5fa38e5
Revises: 7d8b71bf0179
Create Date: 2026-05-05 15:20:00.000000

"""
from alembic import op

revision = '9884a5fa38e5'
down_revision = '7d8b71bf0179'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('feed', schema=None) as batch_op:
        batch_op.create_index(
            'ix_feed_stock_id_releaseTime',
            ['stock_id', 'releaseTime']
        )


def downgrade():
    with op.batch_alter_table('feed', schema=None) as batch_op:
        batch_op.drop_index('ix_feed_stock_id_releaseTime')
