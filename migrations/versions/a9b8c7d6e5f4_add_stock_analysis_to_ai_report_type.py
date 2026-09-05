"""add_stock_analysis_to_ai_report_type

Revision ID: a9b8c7d6e5f4
Revises: ab67d43d772d
Create Date: 2026-06-27 00:00:00.000000

"""
from alembic import op

revision = 'a9b8c7d6e5f4'
down_revision = 'ab67d43d772d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE ai_report MODIFY COLUMN report_type "
        "ENUM('earnings_call', 'news', 'stock_analysis') NOT NULL"
    )


def downgrade():
    op.execute(
        "ALTER TABLE ai_report MODIFY COLUMN report_type "
        "ENUM('earnings_call', 'news') NOT NULL"
    )
