import pytest
from datetime import date
from app.database_setup import MonthRevenue, BasicInformation

# filepath: app/test_database_setup.py

@pytest.fixture
def mock_month_revenue():
    return MonthRevenue(
        id=1,
        stock_id="2330",
        year=2023,
        month="1",
        update_date=date(2023, 1, 31),
        當月營收=1000000,
        上月營收=900000,
        去年當月營收=800000,
        上月比較增減=11.11,
        去年同月增減=25.0,
        當月累計營收=1000000,
        去年累計營收=800000,
        前期比較增減=25.0,
        備註="Test data"
    )

def test_month_revenue_creation(mock_month_revenue):
    assert mock_month_revenue.id == 1
    assert mock_month_revenue.stock_id == "2330"
    assert mock_month_revenue.year == 2023
    assert mock_month_revenue.month == "1"
    assert mock_month_revenue.當月營收 == 1000000
    assert mock_month_revenue.備註 == "Test data"

def test_month_revenue_serialization(mock_month_revenue):
    serialized = mock_month_revenue.serialize
    assert serialized["id"] == 1
    assert serialized["stock_id"] == "2330"
    assert serialized["當月營收"] == 1000000
    assert serialized["備註"] == "Test data"

def test_month_revenue_getitem(mock_month_revenue):
    assert mock_month_revenue["當月營收"] == 1000000
    assert mock_month_revenue["備註"] == "Test data"

def test_month_revenue_setitem(mock_month_revenue):
    mock_month_revenue["當月營收"] = 2000000
    mock_month_revenue["備註"] = "Updated data"
    assert mock_month_revenue.當月營收 == 2000000
    assert mock_month_revenue.備註 == "Updated data"