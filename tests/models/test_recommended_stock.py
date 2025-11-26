import pytest
from datetime import date, timedelta

from app.models.recommended_stock import RecommendedStock
from app.database_setup import BasicInformation


@pytest.fixture
def mock_recommended_stock():
    """Fixture to create a RecommendedStock instance."""
    return RecommendedStock(
        stock_id='2330',
        update_date=date.today(),
        filter_model='月營收近一年次高'
    )


@pytest.mark.usefixtures('test_app')
class TestRecommendedStock:
    """Test suite for RecommendedStock model."""

    def test_instance_creation(self, mock_recommended_stock):
        """Test creation of RecommendedStock instance."""
        assert mock_recommended_stock.stock_id == '2330'
        assert mock_recommended_stock.update_date == date.today()
        assert mock_recommended_stock.filter_model == '月營收近一年次高'

    def test_repr(self, mock_recommended_stock):
        """Test __repr__ method."""
        repr_str = repr(mock_recommended_stock)
        assert 'RecommendedStock' in repr_str
        assert '2330' in repr_str
        assert '月營收近一年次高' in repr_str

    def test_database_operations(self, test_app, sample_basic_info):
        """Test database CRUD operations."""
        with test_app.app_context():
            from app import db

            # Create
            rec_stock = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec_stock)
            db.session.commit()

            # Read
            retrieved = RecommendedStock.query.filter_by(
                stock_id='2330',
                filter_model='月營收近一年次高'
            ).first()
            assert retrieved is not None
            assert retrieved.stock_id == '2330'

            # Update
            retrieved.filter_model = '更新模型'
            db.session.commit()

            updated = RecommendedStock.query.filter_by(stock_id='2330').first()
            assert updated.filter_model == '更新模型'

            # Delete
            db.session.delete(updated)
            db.session.commit()

            deleted = RecommendedStock.query.filter_by(stock_id='2330').first()
            assert deleted is None

    def test_unique_constraint(self, test_app, sample_basic_info):
        """Test unique constraint on stock_id, update_date, filter_model."""
        with test_app.app_context():
            from app import db
            from sqlalchemy.exc import IntegrityError

            # Create first record
            rec1 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec1)
            db.session.commit()

            # Try to create duplicate
            rec2 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Cleanup
            RecommendedStock.query.filter_by(stock_id=sample_basic_info.id).delete()
            db.session.commit()

    def test_same_stock_different_dates(self, test_app, sample_basic_info):
        """Test that same stock can be recommended on different dates."""
        with test_app.app_context():
            from app import db

            today = date.today()
            yesterday = today - timedelta(days=1)

            # Create records for different dates
            rec1 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=today,
                filter_model='月營收近一年次高'
            )
            rec2 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=yesterday,
                filter_model='月營收近一年次高'
            )
            db.session.add_all([rec1, rec2])
            db.session.commit()

            # Query both
            all_recs = RecommendedStock.query.filter_by(
                stock_id='2330',
                filter_model='月營收近一年次高'
            ).all()

            assert len(all_recs) == 2

            # Cleanup
            RecommendedStock.query.filter_by(stock_id='2330').delete()
            db.session.commit()

    def test_same_stock_different_filters(self, test_app, sample_basic_info):
        """Test that same stock can be recommended by different filters."""
        with test_app.app_context():
            from app import db

            # Create records for different filter models
            rec1 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            rec2 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='本益比低於平均'
            )
            db.session.add_all([rec1, rec2])
            db.session.commit()

            # Query both
            all_recs = RecommendedStock.query.filter_by(
                stock_id='2330',
                update_date=date.today()
            ).all()

            assert len(all_recs) == 2
            filter_models = {rec.filter_model for rec in all_recs}
            assert '月營收近一年次高' in filter_models
            assert '本益比低於平均' in filter_models

            # Cleanup
            RecommendedStock.query.filter_by(stock_id='2330').delete()
            db.session.commit()

    def test_query_by_date(self, test_app, sample_basic_info, sample_basic_info_2):
        """Test querying recommendations by date."""
        with test_app.app_context():
            from app import db

            today = date.today()

            # Create multiple recommendations for today
            rec1 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=today,
                filter_model='月營收近一年次高'
            )
            rec2 = RecommendedStock(
                stock_id=sample_basic_info_2.id,
                update_date=today,
                filter_model='月營收近一年次高'
            )
            db.session.add_all([rec1, rec2])
            db.session.commit()

            # Query by date
            today_recs = RecommendedStock.query.filter_by(
                update_date=today
            ).all()

            assert len(today_recs) >= 2
            stock_ids = {rec.stock_id for rec in today_recs}
            assert '2330' in stock_ids
            assert '2317' in stock_ids

            # Cleanup
            RecommendedStock.query.filter(
                RecommendedStock.stock_id.in_(['2330', '2317'])
            ).delete()
            db.session.commit()

    def test_query_by_filter_model(self, test_app, sample_basic_info, sample_basic_info_2):
        """Test querying recommendations by filter model."""
        with test_app.app_context():
            from app import db

            # Create recommendations with same filter model
            rec1 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            rec2 = RecommendedStock(
                stock_id=sample_basic_info_2.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add_all([rec1, rec2])
            db.session.commit()

            # Query by filter model
            filter_recs = RecommendedStock.query.filter_by(
                filter_model='月營收近一年次高'
            ).all()

            assert len(filter_recs) >= 2

            # Cleanup
            RecommendedStock.query.filter(
                RecommendedStock.stock_id.in_(['2330', '2317'])
            ).delete()
            db.session.commit()

    def test_foreign_key_relationship(self, test_app, sample_basic_info):
        """Test foreign key relationship with BasicInformation."""
        with test_app.app_context():
            from app import db

            rec = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec)
            db.session.commit()

            # Test that we can't delete BasicInformation while RecommendedStock exists
            # (This behavior depends on your foreign key constraints)
            # For now, just verify the relationship works

            # Query through relationship
            basic_info = BasicInformation.query.filter_by(id='2330').first()
            assert basic_info is not None

            # Cleanup
            db.session.delete(rec)
            db.session.commit()
