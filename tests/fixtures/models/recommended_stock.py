"""RecommendedStock model fixtures for testing."""
import pytest
from datetime import date
from app import db
from app.models.recommended_stock import RecommendedStock


@pytest.fixture
def sample_recommended_stock(test_app, sample_basic_info):
    """Create sample recommended stock for TSMC (2330)."""
    with test_app.app_context():
        recommended = RecommendedStock(
            stock_id=sample_basic_info.id,
            update_date=date(2024, 3, 15),
            filter_model='value_investing'
        )
        db.session.add(recommended)
        db.session.commit()

        yield recommended

        # Cleanup
        db.session.delete(recommended)
        db.session.commit()


@pytest.fixture
def sample_recommended_stock_list(test_app, sample_basic_info_list):
    """Create multiple recommended stocks for different filter models."""
    with test_app.app_context():
        recommended_list = []
        filter_models = ['value_investing', 'growth_investing', 'dividend_investing']

        for stock in sample_basic_info_list:
            for model in filter_models:
                recommended = RecommendedStock(
                    stock_id=stock.id,
                    update_date=date(2024, 3, 15),
                    filter_model=model
                )
                recommended_list.append(recommended)
                db.session.add(recommended)
        db.session.commit()

        yield recommended_list

        # Cleanup
        for rec in recommended_list:
            db.session.delete(rec)
        db.session.commit()
