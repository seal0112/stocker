"""add last_login_at to user

Revision ID: 53246183bde2
Revises: affcb2eb9acc
Create Date: 2024-12-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53246183bde2'
down_revision = 'affcb2eb9acc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_login_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_login_at')
