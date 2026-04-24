"""add unique constraints to income_sheet and month_revenue

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-01-18

"""
from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def constraint_exists(conn, table_name, constraint_name):
    """Check if a constraint already exists."""
    result = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = :table_name
          AND CONSTRAINT_NAME = :constraint_name
    """), {"table_name": table_name, "constraint_name": constraint_name})
    return result.scalar() > 0


def upgrade():
    conn = op.get_bind()

    # Remove duplicate income_sheet records (keep the one with latest update_date, or highest id)
    conn.execute(text("""
        DELETE t1 FROM income_sheet t1
        INNER JOIN income_sheet t2
        WHERE t1.stock_id = t2.stock_id
          AND t1.year = t2.year
          AND t1.season = t2.season
          AND (t1.update_date < t2.update_date
               OR (t1.update_date = t2.update_date AND t1.id < t2.id))
    """))

    # Remove duplicate month_revenue records (keep the one with latest update_date, or highest id)
    conn.execute(text("""
        DELETE t1 FROM month_revenue t1
        INNER JOIN month_revenue t2
        WHERE t1.stock_id = t2.stock_id
          AND t1.year = t2.year
          AND t1.month = t2.month
          AND (t1.update_date < t2.update_date
               OR (t1.update_date = t2.update_date AND t1.id < t2.id))
    """))

    # Add unique constraint to income_sheet (stock_id, year, season) if not exists
    if not constraint_exists(conn, 'income_sheet', 'uix_income_sheet_stock_year_season'):
        op.create_unique_constraint(
            'uix_income_sheet_stock_year_season',
            'income_sheet',
            ['stock_id', 'year', 'season']
        )

    # Add unique constraint to month_revenue (stock_id, year, month) if not exists
    if not constraint_exists(conn, 'month_revenue', 'uix_month_revenue_stock_year_month'):
        op.create_unique_constraint(
            'uix_month_revenue_stock_year_month',
            'month_revenue',
            ['stock_id', 'year', 'month']
        )


def downgrade():
    conn = op.get_bind()

    if constraint_exists(conn, 'month_revenue', 'uix_month_revenue_stock_year_month'):
        op.drop_constraint('uix_month_revenue_stock_year_month', 'month_revenue', type_='unique')

    if constraint_exists(conn, 'income_sheet', 'uix_income_sheet_stock_year_season'):
        op.drop_constraint('uix_income_sheet_stock_year_season', 'income_sheet', type_='unique')
