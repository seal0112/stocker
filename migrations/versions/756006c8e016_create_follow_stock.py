"""create_follow_stock

Revision ID: 756006c8e016
Revises: 59077070093f
Create Date: 2023-03-19 17:02:13.118929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '756006c8e016'
down_revision = '59077070093f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follow_stock',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.String(length=6), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('last_update_time', sa.DateTime(), nullable=True),
    sa.Column('remove_time', sa.DateTime(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('long_or_short', sa.String(length=10), nullable=False),
    sa.Column('is_delete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['stock_id'], ['basic_information.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follow_stock')
    # ### end Alembic commands ###
