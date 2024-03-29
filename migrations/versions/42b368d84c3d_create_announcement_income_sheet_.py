"""create_announcement_income_sheet_analysis

Revision ID: 42b368d84c3d
Revises: 115dd9b350bf
Create Date: 2024-01-25 16:00:12.795319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42b368d84c3d'
down_revision = '115dd9b350bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('announcement_income_sheet_analysis',
    sa.Column('feed_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.String(length=6)),
    sa.Column('update_date', sa.Date(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('season', sa.Enum('1', '2', '3', '4'), nullable=False),
    sa.Column('processing_failed', sa.Boolean(), nullable=False),
    sa.Column('營業收入合計', sa.BigInteger(), nullable=True),
    sa.Column('營業收入合計年增率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('營業毛利', sa.BigInteger(), nullable=True),
    sa.Column('營業毛利率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('營業毛利率年增率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('營業利益', sa.BigInteger(), nullable=True),
    sa.Column('營業利益率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('營業利益率年增率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('稅前淨利', sa.BigInteger(), nullable=True),
    sa.Column('稅前淨利率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('稅前淨利率年增率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('本期淨利', sa.BigInteger(), nullable=True),
    sa.Column('本期淨利率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('本期淨利率年增率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('母公司業主淨利', sa.BigInteger(), nullable=True),
    sa.Column('基本每股盈餘', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('基本每股盈餘年增率', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['feed_id'], ['feed.id'], ),
    sa.ForeignKeyConstraint(['stock_id'], ['basic_information.id'], ),
    sa.PrimaryKeyConstraint('feed_id')
    )
    with op.batch_alter_table('announcement_income_sheet_analysis', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_announcement_income_sheet_analysis_update_date'), ['update_date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('announcement_income_sheet_analysis', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_announcement_income_sheet_analysis_update_date'))

    op.drop_table('announcement_income_sheet_analysis')
    # ### end Alembic commands ###
