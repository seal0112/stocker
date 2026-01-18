"""Unit tests for MonthRevenue model."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError

from app import db
from app.database_setup import MonthRevenue, BasicInformation


class TestMonthRevenueModel:
    """Tests for MonthRevenue model basic functionality."""

    def test_instance_creation(self):
        """Test MonthRevenue instance creation with all fields."""
        revenue = MonthRevenue(
            stock_id="2330",
            year=2024,
            month="3",
            update_date=date(2024, 4, 10),
            當月營收=200000000000,
            上月營收=195000000000,
            去年當月營收=180000000000,
            上月比較增減=2.56,
            去年同月增減=11.11,
            當月累計營收=585000000000,
            去年累計營收=520000000000,
            前期比較增減=12.5,
            備註="Test note"
        )

        assert revenue.stock_id == "2330"
        assert revenue.year == 2024
        assert revenue.month == "3"
        assert revenue.當月營收 == 200000000000
        assert revenue.上月營收 == 195000000000
        assert revenue.去年當月營收 == 180000000000
        assert revenue.上月比較增減 == 2.56
        assert revenue.去年同月增減 == 11.11
        assert revenue.當月累計營收 == 585000000000
        assert revenue.去年累計營收 == 520000000000
        assert revenue.前期比較增減 == 12.5
        assert revenue.備註 == "Test note"

    def test_serialize_property(self):
        """Test serialize property returns all fields."""
        revenue = MonthRevenue(
            stock_id="2330",
            year=2024,
            month="3",
            當月營收=200000000000,
            備註="Test"
        )

        serialized = revenue.serialize

        assert serialized["stock_id"] == "2330"
        assert serialized["year"] == 2024
        assert serialized["month"] == "3"
        assert serialized["當月營收"] == 200000000000
        assert serialized["備註"] == "Test"
        assert "_sa_instance_state" not in serialized

    def test_getitem_method(self):
        """Test __getitem__ allows dictionary-style access."""
        revenue = MonthRevenue(
            stock_id="2330",
            當月營收=100000000
        )

        assert revenue["stock_id"] == "2330"
        assert revenue["當月營收"] == 100000000

    def test_setitem_method(self):
        """Test __setitem__ allows dictionary-style assignment."""
        revenue = MonthRevenue()

        revenue["stock_id"] = "2330"
        revenue["當月營收"] = 200000000

        assert revenue.stock_id == "2330"
        assert revenue.當月營收 == 200000000


class TestMonthRevenueDatabaseOperations:
    """Tests for MonthRevenue database CRUD operations."""

    def test_create_month_revenue(self, sample_basic_info):
        """Test creating a MonthRevenue record in database."""
        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="5",
            update_date=date(2024, 6, 10),
            當月營收=210000000000,
            上月營收=200000000000,
            去年當月營收=185000000000,
            上月比較增減=5.0,
            去年同月增減=13.51
        )
        db.session.add(revenue)
        db.session.commit()

        assert revenue.id is not None

        # Verify in database
        saved = MonthRevenue.query.filter_by(
            stock_id=sample_basic_info.id,
            year=2025,
            month="5"
        ).first()
        assert saved is not None
        assert saved.當月營收 == 210000000000

        # Cleanup
        db.session.delete(saved)
        db.session.commit()

    def test_read_month_revenue(self, sample_month_revenue):
        """Test reading MonthRevenue from database."""
        revenue = MonthRevenue.query.filter_by(
            id=sample_month_revenue.id
        ).first()

        assert revenue is not None
        assert revenue.stock_id == sample_month_revenue.stock_id
        assert revenue.year == sample_month_revenue.year
        assert revenue.month == sample_month_revenue.month

    def test_update_month_revenue(self, sample_basic_info):
        """Test updating MonthRevenue record."""
        # Create
        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="6",
            當月營收=100000000000
        )
        db.session.add(revenue)
        db.session.commit()

        # Update
        revenue.當月營收 = 150000000000
        revenue.備註 = "Updated"
        db.session.commit()

        # Verify
        updated = MonthRevenue.query.filter_by(id=revenue.id).first()
        assert updated.當月營收 == 150000000000
        assert updated.備註 == "Updated"

        # Cleanup
        db.session.delete(updated)
        db.session.commit()

    def test_delete_month_revenue(self, sample_basic_info):
        """Test deleting MonthRevenue record."""
        # Create
        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="7",
            當月營收=100000000000
        )
        db.session.add(revenue)
        db.session.commit()
        revenue_id = revenue.id

        # Delete
        db.session.delete(revenue)
        db.session.commit()

        # Verify
        deleted = MonthRevenue.query.filter_by(id=revenue_id).first()
        assert deleted is None


class TestMonthRevenueConstraints:
    """Tests for MonthRevenue constraints and validation."""

    def test_unique_constraint_stock_year_month(self, sample_basic_info):
        """Test unique constraint on stock_id + year + month."""
        # Create first record
        revenue1 = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="8",
            當月營收=100000000000
        )
        db.session.add(revenue1)
        db.session.commit()

        # Try to create duplicate
        revenue2 = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="8",
            當月營收=200000000000
        )
        db.session.add(revenue2)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # Cleanup
        MonthRevenue.query.filter_by(
            stock_id=sample_basic_info.id,
            year=2025,
            month="8"
        ).delete()
        db.session.commit()

    def test_valid_month_enum_values(self, sample_basic_info):
        """Test that all valid month values (1-12) work."""
        revenues = []
        for month in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
            revenue = MonthRevenue(
                stock_id=sample_basic_info.id,
                year=2023,
                month=month,
                當月營收=100000000000 + int(month) * 1000000000
            )
            revenues.append(revenue)
            db.session.add(revenue)

        db.session.commit()

        # Verify all 12 months created
        count = MonthRevenue.query.filter_by(
            stock_id=sample_basic_info.id,
            year=2023
        ).count()
        assert count == 12

        # Cleanup
        for rev in revenues:
            db.session.delete(rev)
        db.session.commit()

    def test_foreign_key_constraint(self):
        """Test foreign key constraint with non-existent stock_id."""
        revenue = MonthRevenue(
            stock_id="9999",  # Non-existent stock
            year=2024,
            month="1",
            當月營收=100000000000
        )
        db.session.add(revenue)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


class TestMonthRevenueRelationships:
    """Tests for MonthRevenue relationships."""

    def test_basic_information_relationship(self, sample_basic_info):
        """Test relationship with BasicInformation."""
        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="9",
            當月營收=100000000000
        )
        db.session.add(revenue)
        db.session.commit()

        # Access relationship
        assert revenue.basic_information is not None
        assert revenue.basic_information.id == sample_basic_info.id
        assert revenue.basic_information.公司簡稱 == sample_basic_info.公司簡稱

        # Cleanup
        db.session.delete(revenue)
        db.session.commit()


class TestMonthRevenueQueries:
    """Tests for MonthRevenue query patterns."""

    def test_query_by_stock_id(self, sample_month_revenue_list):
        """Test querying revenues by stock_id."""
        stock_id = sample_month_revenue_list[0].stock_id

        revenues = MonthRevenue.query.filter_by(
            stock_id=stock_id
        ).all()

        assert len(revenues) >= 1
        assert all(r.stock_id == stock_id for r in revenues)

    def test_query_by_year(self, sample_month_revenue_list):
        """Test querying revenues by year."""
        revenues = MonthRevenue.query.filter_by(
            year=2024
        ).all()

        assert all(r.year == 2024 for r in revenues)

    def test_query_ordered_by_date(self, sample_basic_info):
        """Test querying revenues ordered by year and month descending."""
        # Create multiple records (use 2025 to avoid conflict with sample_month_revenue_list)
        revenues = []
        for month in ['1', '3', '6', '9', '12']:
            rev = MonthRevenue(
                stock_id=sample_basic_info.id,
                year=2025,
                month=month,
                當月營收=100000000000
            )
            revenues.append(rev)
            db.session.add(rev)
        db.session.commit()

        # Query ordered
        results = MonthRevenue.query.filter_by(
            stock_id=sample_basic_info.id,
            year=2025
        ).order_by(
            MonthRevenue.month.desc()
        ).all()

        # Verify order (descending by month - Enum sorts by position in enum definition (1,2,3...12), so descending is 12,9,6,3,1
        months = [r.month for r in results]
        assert months == ['12', '9', '6', '3', '1']

        # Cleanup
        for rev in revenues:
            db.session.delete(rev)
        db.session.commit()

    def test_query_limit_60(self, sample_basic_info):
        """Test query pattern used in API (last 60 months)."""
        # Create test data
        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="10",
            當月營收=100000000000
        )
        db.session.add(revenue)
        db.session.commit()

        # Query like the API does
        results = MonthRevenue.query.filter_by(
            stock_id=sample_basic_info.id
        ).order_by(
            MonthRevenue.year.desc()
        ).order_by(
            MonthRevenue.month.desc()
        ).limit(60).all()

        assert len(results) <= 60

        # Cleanup
        db.session.delete(revenue)
        db.session.commit()


class TestMonthRevenueEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_null_optional_fields(self, sample_basic_info):
        """Test that optional fields can be null."""
        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,
            month="11",
            # Only required fields, rest null
        )
        db.session.add(revenue)
        db.session.commit()

        saved = MonthRevenue.query.filter_by(id=revenue.id).first()
        assert saved.當月營收 is None
        assert saved.上月營收 is None
        assert saved.備註 is None

        # Cleanup
        db.session.delete(saved)
        db.session.commit()

    def test_large_revenue_values(self, sample_basic_info):
        """Test that BigInteger can handle large revenue values."""
        large_value = 9999999999999999  # Very large number

        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2025,  # Use different year to avoid conflict with sample_month_revenue_list
            month="12",
            當月營收=large_value
        )
        db.session.add(revenue)
        db.session.commit()

        saved = MonthRevenue.query.filter_by(id=revenue.id).first()
        assert saved.當月營收 == large_value

        # Cleanup
        db.session.delete(saved)
        db.session.commit()

    def test_negative_comparison_values(self, sample_basic_info):
        """Test that negative comparison percentages are handled."""
        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2023,
            month="1",
            當月營收=80000000000,
            上月營收=100000000000,
            上月比較增減=-20.0,  # Negative growth
            去年同月增減=-15.5
        )
        db.session.add(revenue)
        db.session.commit()

        saved = MonthRevenue.query.filter_by(id=revenue.id).first()
        assert saved.上月比較增減 == -20.0
        assert saved.去年同月增減 == -15.5

        # Cleanup
        db.session.delete(saved)
        db.session.commit()

    def test_備註_with_special_characters(self, sample_basic_info):
        """Test 備註 field with special characters."""
        note = "包含特殊字元：！@#$%^&*()、中文、emoji: 📈"

        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2023,
            month="2",
            備註=note
        )
        db.session.add(revenue)
        db.session.commit()

        saved = MonthRevenue.query.filter_by(id=revenue.id).first()
        assert saved.備註 == note

        # Cleanup
        db.session.delete(saved)
        db.session.commit()
