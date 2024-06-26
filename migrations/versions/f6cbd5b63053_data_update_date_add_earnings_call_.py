"""data update date add earnings call column and income_sheet add index to update_date

Revision ID: f6cbd5b63053
Revises: 62be5f006ff5
Create Date: 2024-04-20 11:19:03.034499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6cbd5b63053'
down_revision = '62be5f006ff5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_update_date', schema=None) as batch_op:
        batch_op.add_column(sa.Column('earnings_call_last_update', sa.Date(), nullable=True))

    with op.batch_alter_table('income_sheet', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_income_sheet_update_date'), ['update_date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('income_sheet', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_income_sheet_update_date'))

    with op.batch_alter_table('data_update_date', schema=None) as batch_op:
        batch_op.drop_column('earnings_call_last_update')

    # ### end Alembic commands ###
