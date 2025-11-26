import pytest
from datetime import date

from app.database_setup import BalanceSheet, BasicInformation


@pytest.fixture
def mock_balance_sheet():
    """Fixture to create a BalanceSheet instance."""
    return BalanceSheet(
        stock_id='2330',
        year=2024,
        season='3',
        update_date=date(2024, 11, 14),
        現金及約當現金=1500000000000,
        透過其他綜合損益按公允價值衡量之金融資產流動=200000000000,
        透過損益按公允價值衡量之金融資產流動=50000000000,
        按攤銷後成本衡量之金融資產流動=100000000000,
        存貨=800000000000,
        應收帳款淨額=450000000000,
        應收票據淨額=30000000000,
        流動資產合計=3500000000000,
        透過其他綜合損益按公允價值衡量之金融資產非流動=150000000000,
        透過損益按公允價值衡量之金融資產非流動=80000000000,
        按攤銷後成本衡量之金融資產非流動=60000000000,
        採用權益法之投資=120000000000,
        不動產廠房及設備=5000000000000,
        無形資產=100000000000,
        非流動資產合計=6000000000000,
        資產總計=9500000000000,
        短期借款=200000000000,
        一年或一營業週期內到期長期負債=150000000000,
        應付帳款=600000000000,
        應付票據=50000000000,
        流動負債合計=1200000000000,
        長期借款=500000000000,
        應付公司債=300000000000,
        非流動負債合計=1000000000000,
        負債總計=2200000000000,
        股本合計=2593000000000,
        資本公積合計=1000000000000,
        保留盈餘合計=3500000000000,
        非控制權益=207000000000,
        歸屬於母公司業主之權益=7093000000000,
        權益總計=7300000000000,
        負債及權益總計=9500000000000
    )


@pytest.mark.usefixtures('test_app')
class TestBalanceSheet:
    """Test suite for BalanceSheet model."""

    def test_instance_creation(self, mock_balance_sheet):
        """Test creation of BalanceSheet instance."""
        assert mock_balance_sheet.stock_id == '2330'
        assert mock_balance_sheet.year == 2024
        assert mock_balance_sheet.season == '3'
        assert mock_balance_sheet.資產總計 == 9500000000000
        assert mock_balance_sheet.負債總計 == 2200000000000
        assert mock_balance_sheet.權益總計 == 7300000000000

    def test_balance_equation(self, mock_balance_sheet):
        """Test that the balance sheet equation holds: Assets = Liabilities + Equity."""
        assert mock_balance_sheet.資產總計 == mock_balance_sheet.負債及權益總計
        assert (mock_balance_sheet.負債總計 + mock_balance_sheet.權益總計) == \
               mock_balance_sheet.資產總計

    def test_current_assets_calculation(self, mock_balance_sheet):
        """Test that current assets sum is correct."""
        assert mock_balance_sheet.流動資產合計 == 3500000000000

    def test_non_current_assets_calculation(self, mock_balance_sheet):
        """Test that non-current assets sum is correct."""
        assert mock_balance_sheet.非流動資產合計 == 6000000000000

    def test_total_assets_calculation(self, mock_balance_sheet):
        """Test that total assets equals current + non-current assets."""
        total = mock_balance_sheet.流動資產合計 + mock_balance_sheet.非流動資產合計
        assert total == mock_balance_sheet.資產總計

    def test_serialize(self, mock_balance_sheet):
        """Test the serialize property."""
        serialized = mock_balance_sheet.serialize
        assert isinstance(serialized, dict)
        assert serialized['stock_id'] == '2330'
        assert serialized['資產總計'] == 9500000000000
        assert serialized['負債總計'] == 2200000000000

    def test_getitem(self, mock_balance_sheet):
        """Test __getitem__ method."""
        assert mock_balance_sheet['資產總計'] == 9500000000000
        assert mock_balance_sheet['權益總計'] == 7300000000000

    def test_setitem(self, mock_balance_sheet):
        """Test __setitem__ method."""
        mock_balance_sheet['現金及約當現金'] = 2000000000000
        assert mock_balance_sheet.現金及約當現金 == 2000000000000

    def test_database_operations(self, test_app, sample_basic_info):
        """Test database CRUD operations."""
        with test_app.app_context():
            from app import db

            # Create
            balance = BalanceSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season='3',
                資產總計=9500000000000,
                負債總計=2200000000000,
                權益總計=7300000000000
            )
            db.session.add(balance)
            db.session.commit()

            # Read
            retrieved = BalanceSheet.query.filter_by(
                stock_id='2330',
                year=2024,
                season='3'
            ).first()
            assert retrieved is not None
            assert retrieved.資產總計 == 9500000000000

            # Update
            retrieved.資產總計 = 10000000000000
            db.session.commit()

            updated = BalanceSheet.query.filter_by(stock_id='2330').first()
            assert updated.資產總計 == 10000000000000

            # Cleanup
            db.session.delete(retrieved)
            db.session.commit()

    def test_financial_ratios(self, mock_balance_sheet):
        """Test calculation of common financial ratios."""
        # Current Ratio = Current Assets / Current Liabilities
        current_ratio = mock_balance_sheet.流動資產合計 / mock_balance_sheet.流動負債合計
        assert round(current_ratio, 2) == 2.92

        # Debt to Equity Ratio = Total Liabilities / Total Equity
        debt_to_equity = mock_balance_sheet.負債總計 / mock_balance_sheet.權益總計
        assert round(debt_to_equity, 2) == 0.30

        # Equity Ratio = Total Equity / Total Assets
        equity_ratio = mock_balance_sheet.權益總計 / mock_balance_sheet.資產總計
        assert round(equity_ratio, 2) == 0.77
