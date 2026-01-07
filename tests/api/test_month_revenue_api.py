"""API tests for MonthRevenue endpoints."""
import pytest
import json
from datetime import date

from app import db
from app.database_setup import MonthRevenue


@pytest.mark.usefixtures('test_app')
class TestMonthRevenueGetAPI:
    """Tests for GET /month_revenue/<stock_id> endpoint."""

    def test_get_month_revenue_success(self, test_app, client, sample_month_revenue):
        """Test successful retrieval of month revenue data."""
        with test_app.app_context():
            response = client.get(f'/month_revenue/{sample_month_revenue.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) >= 1

            # Verify response contains expected fields
            first_item = data[0]
            assert 'stock_id' in first_item
            assert 'year' in first_item
            assert 'month' in first_item
            assert '當月營收' in first_item

    def test_get_month_revenue_with_multiple_records(
        self, test_app, client, sample_month_revenue_list
    ):
        """Test retrieval of multiple month revenue records."""
        with test_app.app_context():
            stock_id = sample_month_revenue_list[0].stock_id
            response = client.get(f'/month_revenue/{stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= len(sample_month_revenue_list)

    def test_get_month_revenue_ordered_desc(self, test_app, client, sample_basic_info):
        """Test that results are ordered by year and month descending."""
        with test_app.app_context():
            # Create records for different months
            revenues = []
            for year, month in [(2024, '1'), (2024, '6'), (2023, '12')]:
                rev = MonthRevenue(
                    stock_id=sample_basic_info.id,
                    year=year,
                    month=month,
                    當月營收=100000000000
                )
                revenues.append(rev)
                db.session.add(rev)
            db.session.commit()

            response = client.get(f'/month_revenue/{sample_basic_info.id}')

            assert response.status_code == 200
            data = json.loads(response.data)

            # Verify ordering (newest first)
            if len(data) >= 2:
                for i in range(len(data) - 1):
                    current = (data[i]['year'], data[i]['month'])
                    next_item = (data[i + 1]['year'], data[i + 1]['month'])
                    assert current >= next_item

            # Cleanup
            for rev in revenues:
                db.session.delete(rev)
            db.session.commit()

    def test_get_month_revenue_empty_result(self, test_app, client, sample_basic_info):
        """Test retrieval when no revenue data exists."""
        with test_app.app_context():
            # Ensure no revenue data for this stock
            MonthRevenue.query.filter_by(stock_id=sample_basic_info.id).delete()
            db.session.commit()

            response = client.get(f'/month_revenue/{sample_basic_info.id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []

    def test_get_month_revenue_limit_60(self, test_app, client, sample_basic_info):
        """Test that API returns at most 60 records."""
        with test_app.app_context():
            # The API limits to 60 records (5 years)
            response = client.get(f'/month_revenue/{sample_basic_info.id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) <= 60

    def test_get_month_revenue_nonexistent_stock(self, test_app, client):
        """Test retrieval for non-existent stock returns empty list."""
        with test_app.app_context():
            response = client.get('/month_revenue/9999')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []


@pytest.mark.usefixtures('test_app')
class TestMonthRevenuePostAPI:
    """Tests for POST /month_revenue/<stock_id> endpoint."""

    def test_create_month_revenue_success(self, test_app, client, sample_basic_info):
        """Test successful creation of month revenue record."""
        with test_app.app_context():
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'month': '4',
                '當月營收': 200000000000,
                '上月營收': 195000000000,
                '去年當月營收': 180000000000,
                '上月比較增減': 2.56,
                '去年同月增減': 11.11
            }

            response = client.post(
                f'/month_revenue/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Created'

            # Verify in database
            saved = MonthRevenue.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                month='4'
            ).first()
            assert saved is not None
            assert saved.當月營收 == 200000000000

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_update_existing_month_revenue(self, test_app, client, sample_basic_info):
        """Test updating existing month revenue record."""
        with test_app.app_context():
            # Create initial record
            initial = MonthRevenue(
                stock_id=sample_basic_info.id,
                year=2024,
                month='5',
                當月營收=100000000000
            )
            db.session.add(initial)
            db.session.commit()

            # Update via POST
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'month': '5',
                '當月營收': 150000000000,
                '備註': 'Updated via API'
            }

            response = client.post(
                f'/month_revenue/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Created'

            # Verify update
            updated = MonthRevenue.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                month='5'
            ).first()
            assert updated.當月營收 == 150000000000
            assert updated.備註 == 'Updated via API'

            # Cleanup
            db.session.delete(updated)
            db.session.commit()

    def test_update_no_changes_returns_200(self, test_app, client, sample_basic_info):
        """Test that updating with same values returns 200 OK."""
        with test_app.app_context():
            # Create initial record
            initial = MonthRevenue(
                stock_id=sample_basic_info.id,
                year=2024,
                month='6',
                當月營收=100000000000
            )
            db.session.add(initial)
            db.session.commit()

            # POST with same values
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'month': '6',
                '當月營收': 100000000000
            }

            response = client.post(
                f'/month_revenue/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'OK'

            # Cleanup
            db.session.delete(initial)
            db.session.commit()

    def test_create_month_revenue_missing_body(self, test_app, client, sample_basic_info):
        """Test POST without request body returns 400."""
        with test_app.app_context():
            response = client.post(
                f'/month_revenue/{sample_basic_info.id}',
                content_type='application/json'
            )

            assert response.status_code == 400

    def test_create_month_revenue_invalid_json(self, test_app, client, sample_basic_info):
        """Test POST with invalid JSON returns 400."""
        with test_app.app_context():
            response = client.post(
                f'/month_revenue/{sample_basic_info.id}',
                data='not valid json',
                content_type='application/json'
            )

            assert response.status_code == 400

    def test_create_month_revenue_handles_不適用(self, test_app, client, sample_basic_info):
        """Test that '不適用' values are converted to None."""
        with test_app.app_context():
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'month': '7',
                '當月營收': 100000000000,
                '備註': '不適用'
            }

            response = client.post(
                f'/month_revenue/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201

            # Verify '不適用' was converted to None
            saved = MonthRevenue.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                month='7'
            ).first()
            assert saved.備註 is None

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_create_month_revenue_invalid_stock_returns_400(self, test_app, client):
        """Test POST with invalid stock_id returns 400."""
        with test_app.app_context():
            payload = {
                'stock_id': '9999',  # Non-existent stock
                'year': 2024,
                'month': '1',
                '當月營收': 100000000000
            }

            response = client.post(
                '/month_revenue/9999',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 400


@pytest.mark.usefixtures('test_app')
class TestMonthRevenueAPIIntegration:
    """Integration tests for MonthRevenue API."""

    def test_create_then_get(self, test_app, client, sample_basic_info):
        """Test creating a record then retrieving it."""
        with test_app.app_context():
            # Create
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'month': '8',
                '當月營收': 250000000000,
                '上月營收': 240000000000,
                '去年當月營收': 220000000000,
                '上月比較增減': 4.17,
                '去年同月增減': 13.64
            }

            create_response = client.post(
                f'/month_revenue/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )
            assert create_response.status_code == 201

            # Get
            get_response = client.get(f'/month_revenue/{sample_basic_info.id}')
            assert get_response.status_code == 200

            data = json.loads(get_response.data)
            matching = [d for d in data if d['year'] == 2024 and d['month'] == '8']
            assert len(matching) == 1
            assert matching[0]['當月營收'] == 250000000000

            # Cleanup
            MonthRevenue.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                month='8'
            ).delete()
            db.session.commit()

    def test_create_multiple_months(self, test_app, client, sample_basic_info):
        """Test creating multiple months of revenue data."""
        with test_app.app_context():
            created_months = []

            for month in ['9', '10', '11']:
                payload = {
                    'stock_id': sample_basic_info.id,
                    'year': 2024,
                    'month': month,
                    '當月營收': 100000000000 * int(month)
                }

                response = client.post(
                    f'/month_revenue/{sample_basic_info.id}',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                assert response.status_code == 201
                created_months.append(month)

            # Verify all created
            get_response = client.get(f'/month_revenue/{sample_basic_info.id}')
            data = json.loads(get_response.data)

            for month in created_months:
                matching = [d for d in data if d['year'] == 2024 and d['month'] == month]
                assert len(matching) == 1

            # Cleanup
            MonthRevenue.query.filter(
                MonthRevenue.stock_id == sample_basic_info.id,
                MonthRevenue.year == 2024,
                MonthRevenue.month.in_(created_months)
            ).delete()
            db.session.commit()


@pytest.mark.usefixtures('test_app')
class TestMonthRevenueSerializer:
    """Tests for MonthRevenueSchema serialization."""

    def test_serializer_all_fields(self, test_app, client, sample_month_revenue):
        """Test that serializer includes all expected fields."""
        with test_app.app_context():
            response = client.get(f'/month_revenue/{sample_month_revenue.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1

            item = data[0]
            expected_fields = [
                'id', 'stock_id', 'year', 'month', 'update_date',
                '當月營收', '上月營收', '去年當月營收',
                '上月比較增減', '去年同月增減',
                '當月累計營收', '去年累計營收', '前期比較增減',
                '備註'
            ]

            for field in expected_fields:
                assert field in item, f"Missing field: {field}"

    def test_serializer_date_format(self, test_app, client, sample_month_revenue):
        """Test that dates are properly serialized."""
        with test_app.app_context():
            response = client.get(f'/month_revenue/{sample_month_revenue.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)

            if data:
                update_date = data[0].get('update_date')
                if update_date:
                    # Should be in ISO format (YYYY-MM-DD)
                    assert len(update_date) == 10
                    assert update_date[4] == '-'
                    assert update_date[7] == '-'
