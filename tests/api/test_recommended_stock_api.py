"""API tests for RecommendedStock endpoints."""
import pytest
import json
from datetime import date, timedelta

from app import db
from app.models.recommended_stock import RecommendedStock


# ============================================================================
# Yield-based fixtures for automatic cleanup
# ============================================================================

@pytest.fixture
def temp_recommendation(sample_basic_info):
    """Create a temporary recommendation with automatic cleanup."""
    rec = RecommendedStock(
        stock_id=sample_basic_info.id,
        update_date=date.today(),
        filter_model='月營收近一年次高'
    )
    db.session.add(rec)
    db.session.commit()

    yield rec

    # Auto cleanup after test
    db.session.delete(rec)
    db.session.commit()


@pytest.fixture
def temp_recommendations_multiple_filters(sample_basic_info):
    """Create recommendations with different filter models."""
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

    yield [rec1, rec2]

    # Auto cleanup
    for rec in [rec1, rec2]:
        db.session.delete(rec)
    db.session.commit()


@pytest.fixture
def temp_recommendations_multiple_dates(sample_basic_info):
    """Create recommendations with different dates."""
    yesterday = date.today() - timedelta(days=1)

    rec1 = RecommendedStock(
        stock_id=sample_basic_info.id,
        update_date=date.today(),
        filter_model='月營收近一年次高'
    )
    rec2 = RecommendedStock(
        stock_id=sample_basic_info.id,
        update_date=yesterday,
        filter_model='月營收近一年次高_yesterday'
    )
    db.session.add_all([rec1, rec2])
    db.session.commit()

    yield {'today': rec1, 'yesterday': rec2, 'yesterday_date': yesterday}

    # Auto cleanup
    for rec in [rec1, rec2]:
        db.session.delete(rec)
    db.session.commit()


@pytest.fixture
def temp_recommendations_multiple_stocks(sample_basic_info_list):
    """Create recommendations for multiple stocks."""
    recs = []
    for stock in sample_basic_info_list:
        rec = RecommendedStock(
            stock_id=stock.id,
            update_date=date.today(),
            filter_model='月營收近一年次高'
        )
        recs.append(rec)
        db.session.add(rec)
    db.session.commit()

    yield recs

    # Auto cleanup
    for rec in recs:
        db.session.delete(rec)
    db.session.commit()


# ============================================================================
# Test Classes
# ============================================================================

@pytest.mark.usefixtures('test_app')
class TestRecommendedStockGetAPI:
    """Tests for GET /api/v0/recommended_stock endpoints."""

    def test_get_recommended_stocks_empty(self, client):
        """Test getting recommendations when none exist."""
        response = client.get('/api/v0/recommended_stock')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_recommended_stocks_with_data(self, client, temp_recommendation):
        """Test getting recommendations with data."""
        response = client.get('/api/v0/recommended_stock')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert any(r['stock_id'] == '2330' for r in data)

    def test_get_recommended_stocks_with_filter(self, client, temp_recommendations_multiple_filters):
        """Test filtering recommendations by filter_model."""
        response = client.get('/api/v0/recommended_stock?filter_model=月營收近一年次高')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(r['filter_model'] == '月營收近一年次高' for r in data)

    def test_get_recommended_stocks_with_date(self, client, temp_recommendations_multiple_dates):
        """Test filtering recommendations by date."""
        yesterday = temp_recommendations_multiple_dates['yesterday_date']
        response = client.get(f'/api/v0/recommended_stock?date={yesterday}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(r['update_date'] == str(yesterday) for r in data)

    def test_get_recommended_stocks_with_limit(self, client, temp_recommendations_multiple_stocks):
        """Test limiting number of results."""
        response = client.get('/api/v0/recommended_stock?limit=2')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) <= 2

    def test_get_recommended_stock_detail(self, client, temp_recommendation):
        """Test getting detailed recommendation."""
        response = client.get(f'/api/v0/recommended_stock/{temp_recommendation.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['stock_id'] == '2330'
        assert 'stock_info' in data

    def test_get_recommended_stock_not_found(self, client):
        """Test getting non-existent recommendation."""
        response = client.get('/api/v0/recommended_stock/99999')

        assert response.status_code == 404


@pytest.mark.usefixtures('test_app')
class TestRecommendedStockPostAPI:
    """Tests for POST /api/v0/recommended_stock endpoint."""

    def test_create_recommended_stock(self, client, sample_basic_info):
        """Test creating a new recommendation."""
        payload = {
            'stock_id': sample_basic_info.id,
            'filter_model': '測試模型',
            'update_date': str(date.today())
        }

        response = client.post(
            '/api/v0/recommended_stock',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['stock_id'] == '2330'
        assert data['filter_model'] == '測試模型'

        # Cleanup (use filter to be specific)
        RecommendedStock.query.filter_by(
            stock_id='2330',
            filter_model='測試模型'
        ).delete()
        db.session.commit()

    @pytest.mark.parametrize("payload,description", [
        ({'stock_id': '2330'}, "missing filter_model"),
        ({}, "empty payload"),
    ])
    def test_create_recommended_stock_missing_fields(self, client, payload, description):
        """Test creating recommendation with missing fields."""
        response = client.post(
            '/api/v0/recommended_stock',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400, f"Should fail for {description}"

    def test_create_recommended_stock_invalid_stock(self, client):
        """Test creating recommendation for non-existent stock."""
        payload = {
            'stock_id': '9999',
            'filter_model': '測試模型'
        }

        response = client.post(
            '/api/v0/recommended_stock',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400


@pytest.mark.usefixtures('test_app')
class TestRecommendedStockDeleteAPI:
    """Tests for DELETE /api/v0/recommended_stock endpoint."""

    def test_delete_recommended_stock(self, client, sample_basic_info):
        """Test deleting a recommendation."""
        # Create record to delete
        rec = RecommendedStock(
            stock_id=sample_basic_info.id,
            update_date=date.today(),
            filter_model='to_delete'
        )
        db.session.add(rec)
        db.session.commit()
        rec_id = rec.id

        response = client.delete(f'/api/v0/recommended_stock/{rec_id}')

        assert response.status_code == 200

        deleted = RecommendedStock.query.filter_by(id=rec_id).first()
        assert deleted is None

    def test_delete_recommended_stock_not_found(self, client):
        """Test deleting non-existent recommendation."""
        response = client.delete('/api/v0/recommended_stock/99999')

        assert response.status_code == 404


@pytest.mark.usefixtures('test_app')
class TestRecommendedStockByStockAPI:
    """Tests for GET /api/v0/recommended_stock/stock/<stock_id> endpoint."""

    def test_get_recommendations_by_stock_id(self, client, temp_recommendation):
        """Test getting recommendation history for a stock."""
        stock_id = temp_recommendation.stock_id
        response = client.get(f'/api/v0/recommended_stock/stock/{stock_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert all(r['stock_id'] == '2330' for r in data)


@pytest.mark.usefixtures('test_app')
class TestRecommendedStockStatisticsAPI:
    """Tests for statistics and filter-models endpoints."""

    def test_get_statistics(self, client, temp_recommendation):
        """Test getting recommendation statistics."""
        response = client.get('/api/v0/recommended_stock/statistics')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_recommendations' in data
        assert 'by_filter_model' in data
        assert data['total_recommendations'] >= 1

    def test_get_filter_models(self, client, temp_recommendation):
        """Test getting available filter models."""
        response = client.get('/api/v0/recommended_stock/filter-models')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'filter_models' in data
        assert isinstance(data['filter_models'], list)
