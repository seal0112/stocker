"""BasicInformation model fixtures for testing.

Architecture:
- All fixtures depend on `app_context` for unified context management
- Each fixture ONLY cleans up what it creates
- Child fixtures (month_revenue, income_sheet, etc.) clean up before this fixture
- Pytest handles teardown in reverse dependency order automatically
"""
import pytest
from app import db
from app.database_setup import BasicInformation


@pytest.fixture
def sample_basic_info(app_context):
    """Create a sample BasicInformation record for testing (TSMC 2330).

    Depends on: app_context
    Used by: sample_month_revenue, sample_income_sheet, sample_feed, etc.
    """
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

    # Only delete BasicInformation if we created it
    # Child fixtures clean up their own data before this runs
    if created:
        db.session.delete(stock)
        db.session.commit()


@pytest.fixture
def sample_basic_info_2(app_context):
    """Create a second sample BasicInformation record (Hon Hai 2317).

    Depends on: app_context
    Used by: sample_daily_info_2, etc.
    """
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

    if created:
        db.session.delete(stock)
        db.session.commit()


@pytest.fixture
def sample_basic_info_list(app_context):
    """Create multiple BasicInformation records for batch testing.

    Depends on: app_context
    """
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

    # Only delete what we created
    for stock in stocks:
        if stock.id in created_ids:
            db.session.delete(stock)
    db.session.commit()
