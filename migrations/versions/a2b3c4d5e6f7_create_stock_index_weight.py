"""create_stock_index_weight

Revision ID: a2b3c4d5e6f7
Revises: 9884a5fa38e5
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2b3c4d5e6f7'
down_revision = '9884a5fa38e5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'stock_index_weight',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.String(length=6), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('index_type', sa.String(length=10), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Numeric(10, 4), nullable=True),
        sa.Column('create_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['basic_information.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stock_id', 'year', 'month', 'index_type',
                            name='uix_stock_index_weight'),
    )


def downgrade():
    op.drop_table('stock_index_weight')
