"""BasicInformation model fixtures for testing."""
import pytest
from app.database_setup import BasicInformation


def cleanup_stock_references(db, stock_id):
    """Clean up all records that reference a stock before deleting it."""
    from app.models.feed import Feed
    from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis

    # Delete AnnouncementIncomeSheetAnalysis first (depends on Feed)
    AnnouncementIncomeSheetAnalysis.query.filter_by(stock_id=stock_id).delete()
    # Delete Feeds
    Feed.query.filter_by(stock_id=stock_id).delete()
    db.session.commit()


@pytest.fixture
def sample_basic_info(test_app):
    """Create a sample BasicInformation record for testing (TSMC 2330)."""
    with test_app.app_context():
        from app import db

        stock = BasicInformation(
            id='2330',
            公司名稱='台積電',
            公司簡稱='台積電',
            exchange_type='sii'
        )
        db.session.add(stock)
        db.session.commit()

        yield stock

        # Cleanup - delete related records first to avoid FK constraint
        cleanup_stock_references(db, stock.id)
        db.session.delete(stock)
        db.session.commit()


@pytest.fixture
def sample_basic_info_2(test_app):
    """Create a second sample BasicInformation record (Hon Hai 2317)."""
    with test_app.app_context():
        from app import db

        stock = BasicInformation(
            id='2317',
            公司名稱='鴻海',
            公司簡稱='鴻海',
            exchange_type='sii'
        )
        db.session.add(stock)
        db.session.commit()

        yield stock

        # Cleanup - delete related records first to avoid FK constraint
        cleanup_stock_references(db, stock.id)
        db.session.delete(stock)
        db.session.commit()


@pytest.fixture
def sample_basic_info_list(test_app):
    """Create multiple BasicInformation records for batch testing."""
    with test_app.app_context():
        from app import db

        stocks = [
            BasicInformation(id='2330', 公司名稱='台積電', 公司簡稱='台積電', exchange_type='sii'),
            BasicInformation(id='2317', 公司名稱='鴻海', 公司簡稱='鴻海', exchange_type='sii'),
            BasicInformation(id='2454', 公司名稱='聯發科', 公司簡稱='聯發科', exchange_type='sii'),
        ]
        for stock in stocks:
            db.session.add(stock)
        db.session.commit()

        yield stocks

        # Cleanup - delete related records first to avoid FK constraint
        for stock in stocks:
            cleanup_stock_references(db, stock.id)
            db.session.delete(stock)
        db.session.commit()
