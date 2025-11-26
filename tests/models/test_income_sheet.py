import pytest
from datetime import date
from decimal import Decimal

from app.database_setup import IncomeSheet, BasicInformation


@pytest.fixture
def mock_income_sheet():
    """Fixture to create an IncomeSheet instance."""
    return IncomeSheet(
        stock_id='2330',
        year=2024,
        season='3',
        update_date=date(2024, 11, 14),
        營業收入合計=6238000000,
        營業成本合計=3542000000,
        營業毛利=2696000000,
        營業毛利率=Decimal('43.22'),
        推銷費用=50000000,
        推銷費用率=Decimal('0.80'),
        管理費用=120000000,
        管理費用率=Decimal('1.92'),
        研究發展費用=450000000,
        研究發展費用率=Decimal('7.21'),
        營業費用=620000000,
        營業費用率=Decimal('9.94'),
        營業利益=2076000000,
        營業利益率=Decimal('33.28'),
        營業外收入及支出合計=124000000,
        稅前淨利=2200000000,
        稅前淨利率=Decimal('35.26'),
        所得稅費用=330000000,
        所得稅費用率=Decimal('5.29'),
        本期淨利=1870000000,
        本期淨利率=Decimal('29.97'),
        母公司業主淨利=1870000000,
        基本每股盈餘=7.21,
        稀釋每股盈餘=7.20
    )


@pytest.mark.usefixtures('test_app')
class TestIncomeSheet:
    """Test suite for IncomeSheet model."""

    def test_instance_creation(self, mock_income_sheet):
        """Test creation of IncomeSheet instance."""
        assert mock_income_sheet.stock_id == '2330'
        assert mock_income_sheet.year == 2024
        assert mock_income_sheet.season == '3'
        assert mock_income_sheet.營業收入合計 == 6238000000
        assert mock_income_sheet.營業毛利率 == Decimal('43.22')
        assert mock_income_sheet.基本每股盈餘 == 7.21

    def test_serialize(self, mock_income_sheet):
        """Test the serialize property."""
        serialized = mock_income_sheet.serialize
        assert isinstance(serialized, dict)
        assert serialized['stock_id'] == '2330'
        assert serialized['year'] == 2024
        assert serialized['season'] == '3'
        assert serialized['營業收入合計'] == 6238000000
        assert serialized['基本每股盈餘'] == 7.21

    def test_getitem(self, mock_income_sheet):
        """Test __getitem__ method."""
        assert mock_income_sheet['stock_id'] == '2330'
        assert mock_income_sheet['營業利益率'] == Decimal('33.28')
        assert mock_income_sheet['基本每股盈餘'] == 7.21

    def test_setitem(self, mock_income_sheet):
        """Test __setitem__ method."""
        mock_income_sheet['營業收入合計'] = 7000000000
        mock_income_sheet['基本每股盈餘'] = 8.0

        assert mock_income_sheet.營業收入合計 == 7000000000
        assert mock_income_sheet.基本每股盈餘 == 8.0

    def test_repr(self, mock_income_sheet):
        """Test __repr__ method."""
        mock_income_sheet.id = 1
        repr_str = repr(mock_income_sheet)
        assert '1' in repr_str
        assert '2330' in repr_str
        assert '2024' in repr_str
        assert '3' in repr_str

    def test_database_operations(self, test_app, sample_basic_info):
        """Test database CRUD operations."""
        with test_app.app_context():
            from app import db

            # Create
            income = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season='3',
                營業收入合計=6238000000,
                營業利益率=Decimal('33.28'),
                基本每股盈餘=7.21
            )
            db.session.add(income)
            db.session.commit()

            # Read
            retrieved = IncomeSheet.query.filter_by(
                stock_id='2330',
                year=2024,
                season='3'
            ).first()
            assert retrieved is not None
            assert retrieved.營業收入合計 == 6238000000

            # Update
            retrieved.基本每股盈餘 = 8.0
            db.session.commit()

            updated = IncomeSheet.query.filter_by(stock_id='2330').first()
            assert updated.基本每股盈餘 == 8.0

            # Cleanup
            db.session.delete(retrieved)
            db.session.commit()

    def test_query_by_year_season(self, test_app, sample_basic_info):
        """Test querying by year and season."""
        with test_app.app_context():
            from app import db

            # Create multiple seasons
            for season in ['1', '2', '3', '4']:
                income = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=2024,
                    season=season,
                    營業收入合計=1000000000 * int(season),
                    基本每股盈餘=float(season)
                )
                db.session.add(income)
            db.session.commit()

            # Query specific season
            q3 = IncomeSheet.query.filter_by(
                stock_id='2330',
                year=2024,
                season='3'
            ).first()
            assert q3 is not None
            assert q3.營業收入合計 == 3000000000

            # Query all seasons for a year
            all_seasons = IncomeSheet.query.filter_by(
                stock_id='2330',
                year=2024
            ).order_by(IncomeSheet.season).all()
            assert len(all_seasons) == 4

            # Cleanup
            IncomeSheet.query.filter_by(stock_id='2330').delete()
            db.session.commit()

    def test_profit_margin_calculations(self, mock_income_sheet):
        """Test that profit margins are calculated correctly."""
        # Verify margin calculations
        assert mock_income_sheet.營業毛利率 == Decimal('43.22')
        assert mock_income_sheet.營業利益率 == Decimal('33.28')
        assert mock_income_sheet.稅前淨利率 == Decimal('35.26')
        assert mock_income_sheet.本期淨利率 == Decimal('29.97')
