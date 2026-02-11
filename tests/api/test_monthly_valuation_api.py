"""Tests for MonthlyValuation API endpoints."""
import json
import pytest

from app import db
from app.monthly_valuation.models import MonthlyValuation


@pytest.fixture
def clean_monthly_valuations(test_app, sample_basic_info):
    """Ensure no MonthlyValuation records for test stock before/after test."""
    MonthlyValuation.query.filter_by(stock_id=sample_basic_info.id).delete()
    db.session.commit()
    yield
    MonthlyValuation.query.filter_by(stock_id=sample_basic_info.id).delete()
    db.session.commit()


class TestMonthlyValuationGet:
    """Tests for GET /api/v0/monthly_valuation"""

    def test_get_with_stock_param(self, test_app, client, sample_monthly_valuation):
        """Should return valuations for specified stock."""
        response = client.get('/api/v0/monthly_valuation?stock=2330&years=5')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['stock_id'] == '2330'

    def test_get_default_params(self, test_app, client, sample_basic_info):
        """Should use default stock=2330 and years=5."""
        response = client.get('/api/v0/monthly_valuation')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_invalid_stock_too_long_400(self, test_app, client):
        """Should return 400 for stock parameter longer than 10 chars."""
        response = client.get('/api/v0/monthly_valuation?stock=12345678901')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_get_invalid_years_zero_400(self, test_app, client):
        """Should return 400 for years=0."""
        response = client.get('/api/v0/monthly_valuation?stock=2330&years=0')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_get_invalid_years_over_20_400(self, test_app, client):
        """Should return 400 for years=21."""
        response = client.get('/api/v0/monthly_valuation?stock=2330&years=21')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_get_empty_result(self, test_app, client, sample_basic_info, clean_monthly_valuations):
        """Should return empty list when no valuations exist."""
        response = client.get('/api/v0/monthly_valuation?stock=2330&years=1')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_serializer_fields(self, test_app, client, sample_monthly_valuation):
        """Response should contain expected serializer fields."""
        response = client.get('/api/v0/monthly_valuation?stock=2330')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        item = data[0]
        expected_fields = ['stock_id', 'year', 'month', '本益比', '淨值比', '殖利率', '均價']
        for field in expected_fields:
            assert field in item

    def test_get_decimal_fields_as_strings(self, test_app, client, sample_monthly_valuation):
        """Decimal fields should be serialized as strings."""
        response = client.get('/api/v0/monthly_valuation?stock=2330')
        assert response.status_code == 200
        data = response.get_json()
        item = data[0]
        # Marshmallow Decimal fields with as_string=True
        assert isinstance(item['本益比'], str)
        assert isinstance(item['淨值比'], str)


class TestMonthlyValuationPost:
    """Tests for POST /api/v0/monthly_valuation"""

    def test_create_success_201(self, test_app, client, sample_basic_info, clean_monthly_valuations):
        """Should create new monthly valuation and return 201."""
        payload = {
            'stock_id': '2330',
            'year': 2025,
            'month': '1',
            '本益比': '20.50',
            '淨值比': '5.00',
            '殖利率': '2.00',
            '均價': '600.00'
        }
        response = client.post(
            '/api/v0/monthly_valuation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['stock_id'] == '2330'
        assert data['year'] == 2025
        assert data['month'] == '1'

    def test_create_missing_body_400(self, test_app, client):
        """POST with empty body should return 400."""
        response = client.post(
            '/api/v0/monthly_valuation',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_create_invalid_json_400(self, test_app, client):
        """POST with invalid JSON should return 400."""
        response = client.post(
            '/api/v0/monthly_valuation',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_create_with_decimal_values(self, test_app, client, sample_basic_info, clean_monthly_valuations):
        """POST with decimal values should work correctly."""
        payload = {
            'stock_id': '2330',
            'year': 2025,
            'month': '2',
            '本益比': '15.75',
            '淨值比': '3.25',
            '殖利率': '4.50',
            '均價': '550.00'
        }
        response = client.post(
            '/api/v0/monthly_valuation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['本益比'] == '15.75'
        assert data['淨值比'] == '3.25'


class TestMonthlyValuationPatch:
    """Tests for PATCH /api/v0/monthly_valuation"""

    def test_update_success(self, test_app, client, sample_monthly_valuation):
        """PATCH should update existing valuation."""
        payload = {
            'stock_id': '2330',
            'year': 2024,
            'month': '3',
            '本益比': '22.00'
        }
        response = client.patch(
            '/api/v0/monthly_valuation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['本益比'] == '22.00'

    def test_update_missing_body_400(self, test_app, client):
        """PATCH with empty body should return 400."""
        response = client.patch(
            '/api/v0/monthly_valuation',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_update_invalid_json_400(self, test_app, client):
        """PATCH with invalid JSON should return 400."""
        response = client.patch(
            '/api/v0/monthly_valuation',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_update_multiple_fields(self, test_app, client, sample_monthly_valuation):
        """PATCH should update multiple fields at once."""
        payload = {
            'stock_id': '2330',
            'year': 2024,
            'month': '3',
            '本益比': '25.00',
            '淨值比': '6.00',
            '殖利率': '1.50',
            '均價': '700.00'
        }
        response = client.patch(
            '/api/v0/monthly_valuation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['本益比'] == '25.00'
        assert data['淨值比'] == '6.00'
        assert data['殖利率'] == '1.50'
        assert data['均價'] == '700.00'

    def test_update_preserves_unmodified_fields(self, test_app, client, sample_monthly_valuation):
        """PATCH should only update specified fields, preserving others."""
        # First get the original value
        original_淨值比 = str(sample_monthly_valuation.淨值比)

        payload = {
            'stock_id': '2330',
            'year': 2024,
            'month': '3',
            '本益比': '30.00'
        }
        response = client.patch(
            '/api/v0/monthly_valuation',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['本益比'] == '30.00'
        # 淨值比 should be preserved
        assert data['淨值比'] == original_淨值比
