"""BasicInformation model fixtures for testing."""
import pytest
from app.database_setup import BasicInformation


def cleanup_stock_references(db, stock_id):
    """Clean up all records that reference a stock before deleting it."""
    from app.models.feed import Feed
    from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis
    from app.models.recommended_stock import RecommendedStock
    from app.database_setup import (
        DailyInformation, BalanceSheet, IncomeSheet, MonthRevenue,
        MonthlyValuation, FollowStock
    )

    # Delete in reverse dependency order
    AnnouncementIncomeSheetAnalysis.query.filter_by(stock_id=stock_id).delete()
    Feed.query.filter_by(stock_id=stock_id).delete()
    RecommendedStock.query.filter_by(stock_id=stock_id).delete()
    DailyInformation.query.filter_by(stock_id=stock_id).delete()
    BalanceSheet.query.filter_by(stock_id=stock_id).delete()
    IncomeSheet.query.filter_by(stock_id=stock_id).delete()
    MonthRevenue.query.filter_by(stock_id=stock_id).delete()
    MonthlyValuation.query.filter_by(stock_id=stock_id).delete()
    FollowStock.query.filter_by(stock_id=stock_id).delete()
    db.session.commit()


@pytest.fixture
def sample_basic_info(test_app):
    """Create a sample BasicInformation record for testing (TSMC 2330)."""
    with test_app.app_context():
        from app import db

        # Check if stock already exists (from previous failed test)
        stock = BasicInformation.query.filter_by(id='2330').first()
        created = False
        if not stock:
            stock = BasicInformation(
                id='2330',
                公司名稱='台積電',
                公司簡稱='台積電',
                exchange_type='sii'
            )
            db.session.add(stock)
            db.session.commit()
            created = True

        yield stock

        # Cleanup - delete related records first to avoid FK constraint
        cleanup_stock_references(db, stock.id)
        if created:
            db.session.delete(stock)
            db.session.commit()


@pytest.fixture
def sample_basic_info_2(test_app):
    """Create a second sample BasicInformation record (Hon Hai 2317)."""
    with test_app.app_context():
        from app import db

        # Check if stock already exists (from previous failed test)
        stock = BasicInformation.query.filter_by(id='2317').first()
        created = False
        if not stock:
            stock = BasicInformation(
                id='2317',
                公司名稱='鴻海',
                公司簡稱='鴻海',
                exchange_type='sii'
            )
            db.session.add(stock)
            db.session.commit()
            created = True

        yield stock

        # Cleanup - delete related records first to avoid FK constraint
        cleanup_stock_references(db, stock.id)
        if created:
            db.session.delete(stock)
            db.session.commit()


@pytest.fixture
def sample_basic_info_list(test_app):
    """Create multiple BasicInformation records for batch testing."""
    with test_app.app_context():
        from app import db

        stock_data = [
            ('2330', '台積電', '台積電', 'sii'),
            ('2317', '鴻海', '鴻海', 'sii'),
            ('2454', '聯發科', '聯發科', 'sii'),
        ]
        stocks = []
        created_ids = []

        for stock_id, name, short_name, exchange in stock_data:
            stock = BasicInformation.query.filter_by(id=stock_id).first()
            if not stock:
                stock = BasicInformation(
                    id=stock_id,
                    公司名稱=name,
                    公司簡稱=short_name,
                    exchange_type=exchange
                )
                db.session.add(stock)
                created_ids.append(stock_id)
            stocks.append(stock)

        db.session.commit()

        yield stocks

        # Cleanup - delete related records first to avoid FK constraint
        for stock in stocks:
            cleanup_stock_references(db, stock.id)
            if stock.id in created_ids:
                db.session.delete(stock)
        db.session.commit()
