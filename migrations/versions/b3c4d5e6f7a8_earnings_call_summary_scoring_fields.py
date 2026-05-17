"""earnings_call_summary_scoring_fields

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b3c4d5e6f7a8'
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('earnings_call_summary', 'key_points')

    op.add_column('earnings_call_summary', sa.Column('score', sa.Integer(), nullable=True))
    op.add_column('earnings_call_summary', sa.Column('sentiment', sa.String(20), nullable=True))
    op.add_column('earnings_call_summary', sa.Column('impact_duration', sa.String(20), nullable=True))
    op.add_column('earnings_call_summary', sa.Column('source_reliability', sa.String(20), nullable=True))
    op.add_column('earnings_call_summary', sa.Column('reasoning', sa.Text(), nullable=True))
    op.add_column('earnings_call_summary', sa.Column('news_contributions', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('earnings_call_summary', 'news_contributions')
    op.drop_column('earnings_call_summary', 'reasoning')
    op.drop_column('earnings_call_summary', 'source_reliability')
    op.drop_column('earnings_call_summary', 'impact_duration')
    op.drop_column('earnings_call_summary', 'sentiment')
    op.drop_column('earnings_call_summary', 'score')

    op.add_column('earnings_call_summary', sa.Column('key_points', sa.JSON(), nullable=True))
