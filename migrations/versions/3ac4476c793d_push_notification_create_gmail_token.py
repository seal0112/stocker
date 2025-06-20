"""push_notification create gmail token

Revision ID: 3ac4476c793d
Revises: 8ab2c2675523
Create Date: 2025-06-10 14:22:47.031196

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3ac4476c793d'
down_revision = '8ab2c2675523'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('basicInformation_feed')
    with op.batch_alter_table('push_notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gmail_token', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('gmail', sa.String(length=128), nullable=True))
        batch_op.drop_column('line_notify_token')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('push_notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('line_notify_token', mysql.VARCHAR(length=64), nullable=True))
        batch_op.drop_column('gmail_token')

    op.create_table('basicInformation_feed',
    sa.Column('basic_information_id', mysql.VARCHAR(length=6), nullable=False),
    sa.Column('feed_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['basic_information_id'], ['basic_information.id'], name='basicInformation_feed_ibfk_1'),
    sa.ForeignKeyConstraint(['feed_id'], ['feed.id'], name='basicInformation_feed_ibfk_2'),
    sa.PrimaryKeyConstraint('basic_information_id', 'feed_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
