"""RecommendedStock model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
"""
import pytest
from datetime import date
from app import db
from app.models.recommended_stock import RecommendedStock


@pytest.fixture
def sample_recommended_stock(sample_basic_info):
    """Create sample recommended stock for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
    recommended = RecommendedStock(
        stock_id=sample_basic_info.id,
        update_date=date(2024, 3, 15),
        filter_model='value_investing'
    )
    db.session.add(recommended)
    db.session.commit()

    yield recommended

    # Explicit cleanup
    RecommendedStock.query.filter_by(
        stock_id=sample_basic_info.id,
        update_date=date(2024, 3, 15),
        filter_model='value_investing'
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_recommended_stock_list(sample_basic_info_list):
    """Create multiple recommended stocks for different filter models.

    Depends on: sample_basic_info_list → app_context
    """
    recommended_list = []
    filter_models = ['value_investing', 'growth_investing', 'dividend_investing']
    stock_ids = [stock.id for stock in sample_basic_info_list]

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

    # Explicit cleanup
    RecommendedStock.query.filter(
        RecommendedStock.stock_id.in_(stock_ids),
        RecommendedStock.update_date == date(2024, 3, 15)
    ).delete()
    db.session.commit()
