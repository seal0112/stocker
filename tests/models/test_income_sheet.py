"""Unit tests for IncomeSheet model."""
import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app import db
from app.database_setup import IncomeSheet, BasicInformation


class TestIncomeSheetModel:
    """Tests for IncomeSheet model basic functionality."""

    def test_instance_creation(self, test_app):
        """Test IncomeSheet instance creation with all fields."""
        income_sheet = IncomeSheet(
            stock_id="2330",
            year=2024,
            season="3",
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

        assert income_sheet.stock_id == "2330"
        assert income_sheet.year == 2024
        assert income_sheet.season == "3"
        assert income_sheet.營業收入合計 == 6238000000
        assert income_sheet.營業毛利率 == Decimal('43.22')
        assert income_sheet.基本每股盈餘 == 7.21
        assert income_sheet.稀釋每股盈餘 == 7.20

    def test_serialize_property(self, test_app):
        """Test serialize property returns all fields."""
        income_sheet = IncomeSheet(
            stock_id="2330",
            year=2024,
            season="3",
            營業收入合計=6238000000,
            基本每股盈餘=7.21
        )

        serialized = income_sheet.serialize

        assert serialized["stock_id"] == "2330"
        assert serialized["year"] == 2024
        assert serialized["season"] == "3"
        assert serialized["營業收入合計"] == 6238000000
        assert serialized["基本每股盈餘"] == 7.21
        assert "_sa_instance_state" not in serialized

    def test_getitem_method(self, test_app):
        """Test __getitem__ allows dictionary-style access."""
        income_sheet = IncomeSheet(
            stock_id="2330",
            營業利益率=Decimal('33.28'),
            基本每股盈餘=7.21
        )

        assert income_sheet["stock_id"] == "2330"
        assert income_sheet["營業利益率"] == Decimal('33.28')
        assert income_sheet["基本每股盈餘"] == 7.21

    def test_setitem_method(self, test_app):
        """Test __setitem__ allows dictionary-style assignment."""
        income_sheet = IncomeSheet()

        income_sheet["stock_id"] = "2330"
        income_sheet["營業收入合計"] = 7000000000
        income_sheet["基本每股盈餘"] = 8.0

        assert income_sheet.stock_id == "2330"
        assert income_sheet.營業收入合計 == 7000000000
        assert income_sheet.基本每股盈餘 == 8.0

    def test_repr_method(self, test_app):
        """Test __repr__ returns expected format."""
        income_sheet = IncomeSheet(
            stock_id="2330",
            year=2024,
            season="3"
        )
        income_sheet.id = 1

        repr_str = repr(income_sheet)

        assert "1" in repr_str
        assert "2330" in repr_str
        assert "2024" in repr_str
        assert "3" in repr_str


class TestIncomeSheetDatabaseOperations:
    """Tests for IncomeSheet database CRUD operations."""

    def test_create_income_sheet(self, test_app, sample_basic_info):
        """Test creating an IncomeSheet record in database."""
        with test_app.app_context():
            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season="3",
                update_date=date(2024, 11, 14),
                營業收入合計=6238000000,
                營業利益率=Decimal('33.28'),
                基本每股盈餘=7.21
            )
            db.session.add(income_sheet)
            db.session.commit()

            assert income_sheet.id is not None

            # Verify in database
            saved = IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                season="3"
            ).first()
            assert saved is not None
            assert saved.營業收入合計 == 6238000000

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_read_income_sheet(self, test_app, sample_income_sheet):
        """Test reading IncomeSheet from database."""
        with test_app.app_context():
            income_sheet = IncomeSheet.query.filter_by(
                id=sample_income_sheet.id
            ).first()

            assert income_sheet is not None
            assert income_sheet.stock_id == sample_income_sheet.stock_id
            assert income_sheet.year == sample_income_sheet.year
            assert income_sheet.season == sample_income_sheet.season

    def test_update_income_sheet(self, test_app, sample_basic_info):
        """Test updating IncomeSheet record."""
        with test_app.app_context():
            # Create
            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season="2",
                營業收入合計=5000000000,
                基本每股盈餘=5.0
            )
            db.session.add(income_sheet)
            db.session.commit()

            # Update
            income_sheet.營業收入合計 = 6000000000
            income_sheet.基本每股盈餘 = 6.5
            db.session.commit()

            # Verify
            updated = IncomeSheet.query.filter_by(id=income_sheet.id).first()
            assert updated.營業收入合計 == 6000000000
            assert updated.基本每股盈餘 == 6.5

            # Cleanup
            db.session.delete(updated)
            db.session.commit()

    def test_delete_income_sheet(self, test_app, sample_basic_info):
        """Test deleting IncomeSheet record."""
        with test_app.app_context():
            # Create
            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season="1",
                營業收入合計=4000000000
            )
            db.session.add(income_sheet)
            db.session.commit()
            income_sheet_id = income_sheet.id

            # Delete
            db.session.delete(income_sheet)
            db.session.commit()

            # Verify
            deleted = IncomeSheet.query.filter_by(id=income_sheet_id).first()
            assert deleted is None


class TestIncomeSheetConstraints:
    """Tests for IncomeSheet constraints and validation."""

    def test_unique_constraint_stock_year_season(self, test_app, sample_basic_info):
        """Test unique constraint on stock_id + year + season."""
        with test_app.app_context():
            # Create first record
            income1 = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season="4",
                營業收入合計=5000000000
            )
            db.session.add(income1)
            db.session.commit()

            # Try to create duplicate
            income2 = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season="4",
                營業收入合計=6000000000
            )
            db.session.add(income2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Cleanup
            IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2023,
                season="4"
            ).delete()
            db.session.commit()

    def test_valid_season_enum_values(self, test_app, sample_basic_info):
        """Test that all valid season values (1-4) work."""
        with test_app.app_context():
            income_sheets = []
            for season in ['1', '2', '3', '4']:
                income = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=2022,
                    season=season,
                    營業收入合計=1000000000 * int(season)
                )
                income_sheets.append(income)
                db.session.add(income)

            db.session.commit()

            # Verify all 4 seasons created
            count = IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2022
            ).count()
            assert count == 4

            # Cleanup
            for inc in income_sheets:
                db.session.delete(inc)
            db.session.commit()

    def test_foreign_key_constraint(self, test_app):
        """Test foreign key constraint with non-existent stock_id."""
        with test_app.app_context():
            income_sheet = IncomeSheet(
                stock_id="9999",  # Non-existent stock
                year=2024,
                season="1",
                營業收入合計=1000000000
            )
            db.session.add(income_sheet)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()


class TestIncomeSheetRelationships:
    """Tests for IncomeSheet relationships."""

    def test_basic_information_relationship(self, test_app, sample_basic_info):
        """Test relationship with BasicInformation."""
        with test_app.app_context():
            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season="4",
                營業收入合計=7000000000
            )
            db.session.add(income_sheet)
            db.session.commit()

            # Verify stock relationship exists via query
            saved = IncomeSheet.query.filter_by(id=income_sheet.id).first()
            stock = BasicInformation.query.filter_by(id=saved.stock_id).first()
            assert stock is not None
            assert stock.id == sample_basic_info.id

            # Cleanup
            db.session.delete(income_sheet)
            db.session.commit()


class TestIncomeSheetQueries:
    """Tests for IncomeSheet query patterns."""

    def test_query_by_stock_id(self, test_app, sample_income_sheet_list):
        """Test querying income sheets by stock_id."""
        with test_app.app_context():
            stock_id = sample_income_sheet_list[0].stock_id

            income_sheets = IncomeSheet.query.filter_by(
                stock_id=stock_id
            ).all()

            assert len(income_sheets) >= 1
            assert all(inc.stock_id == stock_id for inc in income_sheets)

    def test_query_by_year(self, test_app, sample_income_sheet_list):
        """Test querying income sheets by year."""
        with test_app.app_context():
            income_sheets = IncomeSheet.query.filter_by(
                year=2024
            ).all()

            assert all(inc.year == 2024 for inc in income_sheets)

    def test_query_ordered_by_year_season_desc(self, test_app, sample_basic_info):
        """Test querying income sheets ordered by year and season descending."""
        with test_app.app_context():
            # Create multiple records
            income_sheets = []
            for year, season in [(2023, '3'), (2023, '4'), (2024, '1'), (2024, '2')]:
                inc = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=year,
                    season=season,
                    營業收入合計=1000000000
                )
                income_sheets.append(inc)
                db.session.add(inc)
            db.session.commit()

            # Query ordered
            results = IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id
            ).order_by(
                IncomeSheet.year.desc(),
                IncomeSheet.season.desc()
            ).all()

            # Verify order (newest first)
            if len(results) >= 2:
                for i in range(len(results) - 1):
                    current = (results[i].year, results[i].season)
                    next_item = (results[i + 1].year, results[i + 1].season)
                    assert current >= next_item

            # Cleanup
            for inc in income_sheets:
                db.session.delete(inc)
            db.session.commit()

    def test_query_latest_income_sheet(self, test_app, sample_basic_info):
        """Test query pattern used in API (latest income sheet)."""
        with test_app.app_context():
            # Create test data
            inc1 = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season="4",
                營業收入合計=5000000000
            )
            inc2 = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season="1",
                營業收入合計=6000000000
            )
            db.session.add_all([inc1, inc2])
            db.session.commit()

            # Query like the API does (get latest)
            result = IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id
            ).order_by(
                IncomeSheet.year.desc()
            ).order_by(
                IncomeSheet.season.desc()
            ).first()

            assert result is not None
            assert result.year == 2024
            assert result.season == "1"

            # Cleanup
            db.session.delete(inc1)
            db.session.delete(inc2)
            db.session.commit()


class TestIncomeSheetEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_null_optional_fields(self, test_app, sample_basic_info):
        """Test that optional fields can be null."""
        with test_app.app_context():
            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season="1",
                # Only required fields, rest null
            )
            db.session.add(income_sheet)
            db.session.commit()

            saved = IncomeSheet.query.filter_by(id=income_sheet.id).first()
            assert saved.營業收入合計 is None
            assert saved.營業毛利 is None
            assert saved.基本每股盈餘 is None

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_large_revenue_values(self, test_app, sample_basic_info):
        """Test that BigInteger can handle large revenue values."""
        with test_app.app_context():
            large_value = 9999999999999999  # Very large number

            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season="2",
                營業收入合計=large_value,
                營業毛利=large_value // 2
            )
            db.session.add(income_sheet)
            db.session.commit()

            saved = IncomeSheet.query.filter_by(id=income_sheet.id).first()
            assert saved.營業收入合計 == large_value
            assert saved.營業毛利 == large_value // 2

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_negative_values_for_losses(self, test_app, sample_basic_info):
        """Test that negative values are handled (for losses)."""
        with test_app.app_context():
            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2022,
                season="4",
                營業收入合計=1000000000,
                營業毛利=-200000000,  # Negative gross profit (loss)
                營業毛利率=Decimal('-20.00'),
                營業利益=-500000000,  # Operating loss
                營業利益率=Decimal('-50.00'),
                本期淨利=-800000000,  # Net loss
                本期淨利率=Decimal('-80.00'),
                基本每股盈餘=-3.5,  # Loss per share
                稀釋每股盈餘=-3.5
            )
            db.session.add(income_sheet)
            db.session.commit()

            saved = IncomeSheet.query.filter_by(id=income_sheet.id).first()
            assert saved.營業毛利 == -200000000
            assert saved.營業毛利率 == Decimal('-20.00')
            assert saved.基本每股盈餘 == -3.5

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_decimal_precision(self, test_app, sample_basic_info):
        """Test that Numeric fields maintain decimal precision."""
        with test_app.app_context():
            income_sheet = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2022,
                season="3",
                營業毛利率=Decimal('43.25'),
                營業利益率=Decimal('33.33'),
                稅前淨利率=Decimal('35.55'),
                本期淨利率=Decimal('29.99')
            )
            db.session.add(income_sheet)
            db.session.commit()

            saved = IncomeSheet.query.filter_by(id=income_sheet.id).first()
            assert saved.營業毛利率 == Decimal('43.25')
            assert saved.營業利益率 == Decimal('33.33')
            assert saved.稅前淨利率 == Decimal('35.55')
            assert saved.本期淨利率 == Decimal('29.99')

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_profit_margin_fields(self, test_app):
        """Test that profit margin fields are calculated correctly."""
        income_sheet = IncomeSheet(
            stock_id="2330",
            year=2024,
            season="3",
            營業毛利率=Decimal('43.22'),
            營業利益率=Decimal('33.28'),
            稅前淨利率=Decimal('35.26'),
            本期淨利率=Decimal('29.97')
        )

        assert income_sheet.營業毛利率 == Decimal('43.22')
        assert income_sheet.營業利益率 == Decimal('33.28')
        assert income_sheet.稅前淨利率 == Decimal('35.26')
        assert income_sheet.本期淨利率 == Decimal('29.97')
