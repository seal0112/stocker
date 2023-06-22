"""change user picture data length

Revision ID: 59077070093f
Revises: 672469063539
Create Date: 2023-03-10 18:15:06.614695

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '59077070093f'
down_revision = '672469063539'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('profile_pic',
               existing_type=mysql.VARCHAR(length=128),
               type_=sa.String(length=512),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('profile_pic',
               existing_type=sa.String(length=512),
               type_=mysql.VARCHAR(length=128),
               existing_nullable=True)

    # ### end Alembic commands ###