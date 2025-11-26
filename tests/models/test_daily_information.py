import pytest
from datetime import date
from decimal import Decimal

from app.database_setup import DailyInformation, BasicInformation


@pytest.fixture
def mock_daily_info():
    """Fixture to create a DailyInformation instance."""
    return DailyInformation(
        stock_id='2330',
        update_date=date(2025, 1, 15),
        本日收盤價=550.0,
        本日漲跌=10.0,
        近四季每股盈餘=28.5,
        本益比=Decimal('19.30'),
        殖利率=2.8,
        股價淨值比=4.2
    )


@pytest.mark.usefixtures('test_app')
class TestDailyInformation:
    """Test suite for DailyInformation model."""

    def test_instance_creation(self, mock_daily_info):
        """Test creation of DailyInformation instance."""
        assert mock_daily_info.stock_id == '2330'
        assert mock_daily_info.本日收盤價 == 550.0
        assert mock_daily_info.本日漲跌 == 10.0
        assert mock_daily_info.近四季每股盈餘 == 28.5
        assert mock_daily_info.本益比 == Decimal('19.30')
        assert mock_daily_info.殖利率 == 2.8
        assert mock_daily_info.股價淨值比 == 4.2

    def test_serialize(self, mock_daily_info):
        """Test the serialize property."""
        serialized = mock_daily_info.serialize
        assert isinstance(serialized, dict)
        assert serialized['stock_id'] == '2330'
        assert serialized['本日收盤價'] == 550.0
        assert serialized['近四季每股盈餘'] == 28.5

    def test_getitem(self, mock_daily_info):
        """Test __getitem__ method."""
        assert mock_daily_info['stock_id'] == '2330'
        assert mock_daily_info['本日收盤價'] == 550.0
        assert mock_daily_info['殖利率'] == 2.8

    def test_setitem(self, mock_daily_info):
        """Test __setitem__ method."""
        mock_daily_info['本日收盤價'] = 560.0
        mock_daily_info['殖利率'] = 3.0

        assert mock_daily_info.本日收盤價 == 560.0
        assert mock_daily_info.殖利率 == 3.0

    def test_database_relationship(self, test_app, sample_basic_info):
        """Test relationship with BasicInformation."""
        with test_app.app_context():
            from app import db

            daily_info = DailyInformation(
                stock_id=sample_basic_info.id,
                本日收盤價=550.0,
                update_date=date.today()
            )
            db.session.add(daily_info)
            db.session.commit()

            # Verify relationship
            retrieved = DailyInformation.query.filter_by(stock_id='2330').first()
            assert retrieved is not None
            assert retrieved.basic_information.公司名稱 == '台積電'

            # Cleanup
            db.session.delete(daily_info)
            db.session.commit()

    def test_primary_key_constraint(self, test_app, sample_basic_info):
        """Test that stock_id is unique (primary key)."""
        with test_app.app_context():
            from app import db
            from sqlalchemy.exc import IntegrityError

            daily1 = DailyInformation(
                stock_id=sample_basic_info.id,
                本日收盤價=550.0
            )
            db.session.add(daily1)
            db.session.commit()

            # Try to add duplicate
            daily2 = DailyInformation(
                stock_id=sample_basic_info.id,
                本日收盤價=560.0
            )
            db.session.add(daily2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Cleanup
            DailyInformation.query.filter_by(stock_id=sample_basic_info.id).delete()
            db.session.commit()
