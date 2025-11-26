import pytest
from datetime import datetime
from decimal import Decimal

from app.monthly_valuation.models import MonthlyValuation
from app.database_setup import BasicInformation


@pytest.fixture
def mock_monthly_valuation():
    """Fixture to create a MonthlyValuation instance."""
    return MonthlyValuation(
        stock_id='2330',
        year=2024,
        month='10',
        本益比=Decimal('18.50'),
        淨值比=Decimal('4.20'),
        殖利率=Decimal('2.80'),
        均價=Decimal('520.50')
    )


@pytest.mark.usefixtures('test_app')
class TestMonthlyValuation:
    """Test suite for MonthlyValuation model."""

    def test_instance_creation(self, mock_monthly_valuation):
        """Test creation of MonthlyValuation instance."""
        assert mock_monthly_valuation.stock_id == '2330'
        assert mock_monthly_valuation.year == 2024
        assert mock_monthly_valuation.month == '10'
        assert mock_monthly_valuation.本益比 == Decimal('18.50')
        assert mock_monthly_valuation.淨值比 == Decimal('4.20')
        assert mock_monthly_valuation.殖利率 == Decimal('2.80')
        assert mock_monthly_valuation.均價 == Decimal('520.50')

    def test_repr(self, mock_monthly_valuation):
        """Test __repr__ method."""
        repr_str = repr(mock_monthly_valuation)
        assert 'MonthlyValuation' in repr_str
        assert '2330' in repr_str
        assert '2024' in repr_str
        assert '10' in repr_str

    def test_getitem(self, mock_monthly_valuation):
        """Test __getitem__ method."""
        assert mock_monthly_valuation['本益比'] == Decimal('18.50')
        assert mock_monthly_valuation['均價'] == Decimal('520.50')

    def test_setitem(self, mock_monthly_valuation):
        """Test __setitem__ method."""
        mock_monthly_valuation['本益比'] = Decimal('20.00')
        mock_monthly_valuation['均價'] = Decimal('550.00')

        assert mock_monthly_valuation.本益比 == Decimal('20.00')
        assert mock_monthly_valuation.均價 == Decimal('550.00')

    def test_database_operations(self, test_app, sample_basic_info):
        """Test database CRUD operations."""
        with test_app.app_context():
            from app import db

            # Create
            valuation = MonthlyValuation(
                stock_id=sample_basic_info.id,
                year=2024,
                month='10',
                本益比=Decimal('18.50'),
                均價=Decimal('520.50')
            )
            db.session.add(valuation)
            db.session.commit()

            # Read
            retrieved = MonthlyValuation.query.filter_by(
                stock_id='2330',
                year=2024,
                month='10'
            ).first()
            assert retrieved is not None
            assert retrieved.本益比 == Decimal('18.50')

            # Update
            retrieved.本益比 = Decimal('19.00')
            db.session.commit()

            updated = MonthlyValuation.query.filter_by(
                stock_id='2330',
                year=2024,
                month='10'
            ).first()
            assert updated.本益比 == Decimal('19.00')

            # Cleanup
            db.session.delete(retrieved)
            db.session.commit()

    def test_unique_constraint(self, test_app, sample_basic_info):
        """Test unique constraint on stock_id, year, month."""
        with test_app.app_context():
            from app import db
            from sqlalchemy.exc import IntegrityError

            # Create first record
            val1 = MonthlyValuation(
                stock_id=sample_basic_info.id,
                year=2024,
                month='10',
                本益比=Decimal('18.50')
            )
            db.session.add(val1)
            db.session.commit()

            # Try to create duplicate
            val2 = MonthlyValuation(
                stock_id=sample_basic_info.id,
                year=2024,
                month='10',
                本益比=Decimal('19.00')
            )
            db.session.add(val2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Cleanup
            MonthlyValuation.query.filter_by(stock_id=sample_basic_info.id).delete()
            db.session.commit()

    def test_query_by_year(self, test_app, sample_basic_info):
        """Test querying all months for a specific year."""
        with test_app.app_context():
            from app import db

            # Create data for multiple months
            for month in range(1, 13):
                valuation = MonthlyValuation(
                    stock_id=sample_basic_info.id,
                    year=2024,
                    month=str(month),
                    本益比=Decimal('18.00') + Decimal(str(month * 0.1)),
                    均價=Decimal('500.00') + Decimal(str(month * 5))
                )
                db.session.add(valuation)
            db.session.commit()

            # Query all months for 2024
            all_months = MonthlyValuation.query.filter_by(
                stock_id='2330',
                year=2024
            ).order_by(MonthlyValuation.month).all()

            assert len(all_months) == 12
            assert all_months[0].month == '1'
            assert all_months[11].month == '12'

            # Cleanup
            MonthlyValuation.query.filter_by(stock_id='2330').delete()
            db.session.commit()

    def test_query_recent_months(self, test_app, sample_basic_info):
        """Test querying recent N months."""
        with test_app.app_context():
            from app import db

            # Create data for 12 months
            for month in range(1, 13):
                valuation = MonthlyValuation(
                    stock_id=sample_basic_info.id,
                    year=2024,
                    month=str(month),
                    本益比=Decimal('18.00'),
                    均價=Decimal('500.00')
                )
                db.session.add(valuation)
            db.session.commit()

            # Query recent 6 months
            recent = MonthlyValuation.query.filter_by(
                stock_id='2330',
                year=2024
            ).order_by(
                MonthlyValuation.year.desc(),
                MonthlyValuation.month.desc()
            ).limit(6).all()

            assert len(recent) == 6
            assert recent[0].month == '9'  # Most recent (excluding 10, 11, 12 as strings)

            # Cleanup
            MonthlyValuation.query.filter_by(stock_id='2330').delete()
            db.session.commit()

    def test_create_time_auto_set(self, test_app, sample_basic_info):
        """Test that create_time is automatically set."""
        with test_app.app_context():
            from app import db

            valuation = MonthlyValuation(
                stock_id=sample_basic_info.id,
                year=2024,
                month='10',
                本益比=Decimal('18.50')
            )
            db.session.add(valuation)
            db.session.commit()

            # Retrieve and check create_time
            retrieved = MonthlyValuation.query.filter_by(
                stock_id='2330',
                year=2024,
                month='10'
            ).first()

            assert retrieved.create_time is not None
            assert isinstance(retrieved.create_time, datetime)

            # Cleanup
            db.session.delete(retrieved)
            db.session.commit()

    def test_valuation_metrics(self, mock_monthly_valuation):
        """Test that valuation metrics are within reasonable ranges."""
        # PE ratio should be positive
        assert mock_monthly_valuation.本益比 > 0

        # PB ratio should be positive
        assert mock_monthly_valuation.淨值比 > 0

        # Dividend yield should be between 0 and 100%
        assert 0 <= mock_monthly_valuation.殖利率 <= 100

        # Average price should be positive
        assert mock_monthly_valuation.均價 > 0
