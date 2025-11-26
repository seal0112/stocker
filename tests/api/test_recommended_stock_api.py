import pytest
import json
from datetime import date, timedelta

from app.models.recommended_stock import RecommendedStock


@pytest.mark.usefixtures('test_app')
class TestRecommendedStockAPI:
    """Test suite for Recommended Stock API endpoints."""

    def test_get_recommended_stocks_empty(self, test_app, client):
        """Test getting recommendations when none exist."""
        with test_app.app_context():
            response = client.get('/api/v0/recommended_stock')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_get_recommended_stocks_with_data(
        self, test_app, client, sample_basic_info
    ):
        """Test getting recommendations with data."""
        with test_app.app_context():
            from app import db

            # Create test data
            rec = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec)
            db.session.commit()

            # Test GET
            response = client.get('/api/v0/recommended_stock')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1
            assert any(r['stock_id'] == '2330' for r in data)

            # Cleanup
            db.session.delete(rec)
            db.session.commit()

    def test_get_recommended_stocks_with_filter(
        self, test_app, client, sample_basic_info
    ):
        """Test filtering recommendations by filter_model."""
        with test_app.app_context():
            from app import db

            # Create test data with different filter models
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

            # Test with filter
            response = client.get('/api/v0/recommended_stock?filter_model=月營收近一年次高')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert all(r['filter_model'] == '月營收近一年次高' for r in data)

            # Cleanup
            RecommendedStock.query.filter_by(stock_id='2330').delete()
            db.session.commit()

    def test_get_recommended_stocks_with_date(
        self, test_app, client, sample_basic_info
    ):
        """Test filtering recommendations by date."""
        with test_app.app_context():
            from app import db

            yesterday = date.today() - timedelta(days=1)

            # Create test data for different dates
            rec1 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            rec2 = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=yesterday,
                filter_model='月營收近一年次高'
            )
            db.session.add_all([rec1, rec2])
            db.session.commit()

            # Test with date filter
            response = client.get(f'/api/v0/recommended_stock?date={yesterday}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert all(r['update_date'] == str(yesterday) for r in data)

            # Cleanup
            RecommendedStock.query.filter_by(stock_id='2330').delete()
            db.session.commit()

    def test_get_recommended_stocks_with_limit(
        self, test_app, client, sample_basic_info_list
    ):
        """Test limiting number of results."""
        with test_app.app_context():
            from app import db

            # Create multiple recommendations
            for stock in sample_basic_info_list:
                rec = RecommendedStock(
                    stock_id=stock.id,
                    update_date=date.today(),
                    filter_model='月營收近一年次高'
                )
                db.session.add(rec)
            db.session.commit()

            # Test with limit
            response = client.get('/api/v0/recommended_stock?limit=2')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) <= 2

            # Cleanup
            RecommendedStock.query.filter(
                RecommendedStock.stock_id.in_(['2330', '2317', '2454'])
            ).delete()
            db.session.commit()

    def test_get_recommended_stock_detail(
        self, test_app, client, sample_basic_info
    ):
        """Test getting detailed recommendation."""
        with test_app.app_context():
            from app import db

            rec = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec)
            db.session.commit()

            # Test GET by ID
            response = client.get(f'/api/v0/recommended_stock/{rec.id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['stock_id'] == '2330'
            assert 'stock_info' in data

            # Cleanup
            db.session.delete(rec)
            db.session.commit()

    def test_get_recommended_stock_not_found(self, test_app, client):
        """Test getting non-existent recommendation."""
        with test_app.app_context():
            response = client.get('/api/v0/recommended_stock/99999')

            assert response.status_code == 404

    def test_create_recommended_stock(self, test_app, client, sample_basic_info):
        """Test creating a new recommendation."""
        with test_app.app_context():
            from app import db

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

            # Cleanup
            RecommendedStock.query.filter_by(
                stock_id='2330',
                filter_model='測試模型'
            ).delete()
            db.session.commit()

    def test_create_recommended_stock_missing_fields(self, test_app, client):
        """Test creating recommendation with missing fields."""
        with test_app.app_context():
            payload = {
                'stock_id': '2330'
                # Missing filter_model
            }

            response = client.post(
                '/api/v0/recommended_stock',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 400

    def test_create_recommended_stock_invalid_stock(self, test_app, client):
        """Test creating recommendation for non-existent stock."""
        with test_app.app_context():
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

    def test_delete_recommended_stock(self, test_app, client, sample_basic_info):
        """Test deleting a recommendation."""
        with test_app.app_context():
            from app import db

            rec = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec)
            db.session.commit()
            rec_id = rec.id

            # Test DELETE
            response = client.delete(f'/api/v0/recommended_stock/{rec_id}')

            assert response.status_code == 200

            # Verify deleted
            deleted = RecommendedStock.query.filter_by(id=rec_id).first()
            assert deleted is None

    def test_delete_recommended_stock_not_found(self, test_app, client):
        """Test deleting non-existent recommendation."""
        with test_app.app_context():
            response = client.delete('/api/v0/recommended_stock/99999')

            assert response.status_code == 404

    def test_get_recommendations_by_stock_id(
        self, test_app, client, sample_basic_info
    ):
        """Test getting recommendation history for a stock."""
        with test_app.app_context():
            from app import db

            # Create test data
            rec = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec)
            db.session.commit()

            # Test GET by stock_id
            response = client.get(f'/api/v0/recommended_stock/stock/{sample_basic_info.id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1
            assert all(r['stock_id'] == '2330' for r in data)

            # Cleanup
            db.session.delete(rec)
            db.session.commit()

    def test_get_statistics(self, test_app, client, sample_basic_info):
        """Test getting recommendation statistics."""
        with test_app.app_context():
            from app import db

            # Create test data
            rec = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec)
            db.session.commit()

            # Test GET statistics
            response = client.get('/api/v0/recommended_stock/statistics')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'total_recommendations' in data
            assert 'by_filter_model' in data
            assert data['total_recommendations'] >= 1

            # Cleanup
            db.session.delete(rec)
            db.session.commit()

    def test_get_filter_models(self, test_app, client, sample_basic_info):
        """Test getting available filter models."""
        with test_app.app_context():
            from app import db

            # Create test data
            rec = RecommendedStock(
                stock_id=sample_basic_info.id,
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            db.session.add(rec)
            db.session.commit()

            # Test GET filter models
            response = client.get('/api/v0/recommended_stock/filter-models')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'filter_models' in data
            assert isinstance(data['filter_models'], list)

            # Cleanup
            db.session.delete(rec)
            db.session.commit()
