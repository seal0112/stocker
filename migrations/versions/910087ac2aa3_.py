"""empty message

Revision ID: 910087ac2aa3
Revises: b774353eb528
Create Date: 2023-07-15 14:46:23.887541

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '910087ac2aa3'
down_revision = 'b774353eb528'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feed', schema=None) as batch_op:
        batch_op.alter_column('link',
               existing_type=mysql.TEXT(),
               type_=sa.String(length=600),
               existing_nullable=False)
        batch_op.create_unique_constraint(None, ['link'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feed', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('link',
               existing_type=sa.String(length=600),
               type_=mysql.TEXT(),
               existing_nullable=False)

    # ### end Alembic commands ###
