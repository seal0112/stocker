"""AnnouncementIncomeSheetAnalysis model fixtures for testing.

Architecture:
- Depends on sample_feed (which depends on sample_basic_info → app_context)
- Each fixture cleans up ONLY the records it creates
"""
import pytest
from datetime import date
from app import db
from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis


@pytest.fixture
def sample_announcement_income_sheet_analysis(sample_feed):
    """Create a sample AnnouncementIncomeSheetAnalysis record for testing.

    Depends on: sample_feed → sample_basic_info → app_context
    """
    analysis = AnnouncementIncomeSheetAnalysis(
        feed_id=sample_feed.id,
        stock_id=sample_feed.stock_id,
        update_date=date(2024, 3, 15),
        year=2024,
        season='1',
        processing_failed=False,
        營業收入合計=1000000000,
        營業收入合計年增率=10.5,
        營業毛利=300000000,
        營業毛利率=30.0,
        營業毛利率年增率=2.5,
        營業利益=200000000,
        營業利益率=20.0,
        營業利益率年增率=1.5,
        稅前淨利=180000000,
        稅前淨利率=18.0,
        稅前淨利率年增率=1.2,
        本期淨利=150000000,
        本期淨利率=15.0,
        本期淨利率年增率=1.0,
        母公司業主淨利=145000000,
        基本每股盈餘=5.5,
        基本每股盈餘年增率=8.0,
        本業佔比=111.11
    )
    db.session.add(analysis)
    db.session.commit()

    yield analysis

    # Explicit cleanup
    AnnouncementIncomeSheetAnalysis.query.filter_by(
        feed_id=sample_feed.id
    ).delete()
    db.session.commit()
