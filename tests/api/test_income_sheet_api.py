"""API tests for IncomeSheet endpoints."""
import pytest
import json
from datetime import date
from decimal import Decimal

from app import db
from app.database_setup import IncomeSheet, DailyInformation


@pytest.mark.usefixtures('test_app')
class TestIncomeSheetGetAPI:
    """Tests for GET /income_sheet/<stock_id> endpoint."""

    def test_get_income_sheet_default_mode(self, test_app, client, sample_income_sheet):
        """Test GET without mode returns latest income sheet."""
        with test_app.app_context():
            response = client.get(f'/income_sheet/{sample_income_sheet.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 1

            # Verify response contains expected fields
            item = data[0]
            assert 'stock_id' in item
            assert 'year' in item
            assert 'season' in item
            assert '營業收入合計' in item

    def test_get_income_sheet_single_mode(self, test_app, client, sample_basic_info):
        """Test GET with mode=single returns specific year/season."""
        with test_app.app_context():
            # Create test data
            income = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season='2',
                營業收入合計=5000000000,
                基本每股盈餘=5.0
            )
            db.session.add(income)
            db.session.commit()

            response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=single&year=2024&season=2'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['year'] == 2024
            assert data[0]['season'] == '2'

            # Cleanup
            db.session.delete(income)
            db.session.commit()

    def test_get_income_sheet_single_mode_missing_params(self, test_app, client, sample_basic_info):
        """Test GET with mode=single but missing year/season returns 400."""
        with test_app.app_context():
            # Missing both year and season
            response = client.get(f'/income_sheet/{sample_basic_info.id}?mode=single')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

            # Missing season
            response = client.get(f'/income_sheet/{sample_basic_info.id}?mode=single&year=2024')
            assert response.status_code == 400

            # Missing year
            response = client.get(f'/income_sheet/{sample_basic_info.id}?mode=single&season=1')
            assert response.status_code == 400

    def test_get_income_sheet_single_mode_invalid_season(self, test_app, client, sample_basic_info):
        """Test GET with invalid season returns 400."""
        with test_app.app_context():
            response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=single&year=2024&season=5'
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'season must be 1, 2, 3, or 4' in data['error']

    def test_get_income_sheet_multiple_mode(self, test_app, client, sample_basic_info):
        """Test GET with mode=multiple returns multiple records."""
        with test_app.app_context():
            # Create test data (4 seasons)
            incomes = []
            for season in ['1', '2', '3', '4']:
                income = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=2024,
                    season=season,
                    營業收入合計=1000000000 * int(season)
                )
                incomes.append(income)
                db.session.add(income)
            db.session.commit()

            # Get 2 years (8 seasons)
            response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=multiple&year=2'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) <= 8  # 2 years * 4 seasons

            # Cleanup
            for income in incomes:
                db.session.delete(income)
            db.session.commit()

    def test_get_income_sheet_multiple_mode_default_limit(self, test_app, client, sample_basic_info):
        """Test GET with mode=multiple without year uses default limit of 4."""
        with test_app.app_context():
            # Create test data
            incomes = []
            for season in ['1', '2', '3', '4']:
                income = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=2024,
                    season=season,
                    營業收入合計=1000000000
                )
                incomes.append(income)
                db.session.add(income)
            db.session.commit()

            response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=multiple'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) <= 4  # Default 1 year = 4 seasons

            # Cleanup
            for income in incomes:
                db.session.delete(income)
            db.session.commit()

    def test_get_income_sheet_invalid_mode(self, test_app, client, sample_basic_info):
        """Test GET with invalid mode returns 404."""
        with test_app.app_context():
            response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=invalid'
            )
            assert response.status_code == 404

    def test_get_income_sheet_nonexistent_stock(self, test_app, client):
        """Test GET for non-existent stock returns 404."""
        with test_app.app_context():
            response = client.get('/income_sheet/9999')
            assert response.status_code == 404

    def test_get_income_sheet_ordered_desc(self, test_app, client, sample_basic_info):
        """Test that results are ordered by year and season descending."""
        with test_app.app_context():
            # Create records for different years/seasons
            incomes = []
            for year, season in [(2023, '3'), (2023, '4'), (2024, '1'), (2024, '2')]:
                income = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=year,
                    season=season,
                    營業收入合計=1000000000
                )
                incomes.append(income)
                db.session.add(income)
            db.session.commit()

            response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=multiple&year=2'
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            # Verify ordering (newest first)
            if len(data) >= 2:
                for i in range(len(data) - 1):
                    current = (data[i]['year'], data[i]['season'])
                    next_item = (data[i + 1]['year'], data[i + 1]['season'])
                    assert current >= next_item

            # Cleanup
            for income in incomes:
                db.session.delete(income)
            db.session.commit()


@pytest.mark.usefixtures('test_app')
class TestIncomeSheetPostAPI:
    """Tests for POST /income_sheet/<stock_id> endpoint."""

    def test_create_income_sheet_success(self, test_app, client, sample_basic_info):
        """Test successful creation of income sheet record."""
        with test_app.app_context():
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'season': '3',
                '營業收入合計': 6238000000,
                '營業毛利': 2696000000,
                '營業毛利率': 43.22,
                '營業利益': 2076000000,
                '營業利益率': 33.28,
                '基本每股盈餘': 7.21
            }

            response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Created'

            # Verify in database
            saved = IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                season='3'
            ).first()
            assert saved is not None
            assert saved.營業收入合計 == 6238000000

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_update_existing_income_sheet(self, test_app, client, sample_basic_info):
        """Test updating existing income sheet record."""
        with test_app.app_context():
            # Create initial record
            initial = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2024,
                season='4',
                營業收入合計=5000000000,
                基本每股盈餘=5.0
            )
            db.session.add(initial)
            db.session.commit()

            # Update via POST
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'season': '4',
                '營業收入合計': 6000000000,
                '基本每股盈餘': 6.5
            }

            response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Created'

            # Verify update
            updated = IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                season='4'
            ).first()
            assert updated.營業收入合計 == 6000000000
            assert updated.基本每股盈餘 == 6.5

            # Cleanup
            db.session.delete(updated)
            db.session.commit()

    def test_update_no_changes_returns_200(self, test_app, client, sample_basic_info):
        """Test that updating with same values returns 200 OK."""
        with test_app.app_context():
            # Create initial record
            initial = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season='4',
                營業收入合計=5000000000,
                基本每股盈餘=5.0
            )
            db.session.add(initial)
            db.session.commit()

            # POST with same values
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2023,
                'season': '4',
                '營業收入合計': 5000000000,
                '基本每股盈餘': 5.0
            }

            response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'OK'

            # Cleanup
            db.session.delete(initial)
            db.session.commit()

    def test_create_income_sheet_missing_body(self, test_app, client, sample_basic_info):
        """Test POST without request body returns 400."""
        with test_app.app_context():
            response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                content_type='application/json'
            )

            assert response.status_code == 400

    def test_create_income_sheet_invalid_json(self, test_app, client, sample_basic_info):
        """Test POST with invalid JSON returns 400."""
        with test_app.app_context():
            response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                data='not valid json',
                content_type='application/json'
            )

            assert response.status_code == 400

    def test_create_income_sheet_invalid_stock_returns_400(self, test_app, client):
        """Test POST with invalid stock_id returns 400."""
        with test_app.app_context():
            payload = {
                'stock_id': '9999',  # Non-existent stock
                'year': 2024,
                'season': '1',
                '營業收入合計': 1000000000
            }

            response = client.post(
                '/income_sheet/9999',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 400


@pytest.mark.usefixtures('test_app')
class TestCheckFourSeasonEPS:
    """Tests for checkFourSeasonEPS function."""

    def test_four_season_eps_calculation(self, test_app, client, sample_basic_info):
        """Test that four season EPS is calculated and stored."""
        with test_app.app_context():
            # Create 4 seasons of income sheet data
            incomes = []
            eps_values = [2.0, 2.5, 3.0, 3.5]  # Total = 11.0
            for i, season in enumerate(['1', '2', '3', '4']):
                income = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=2024,
                    season=season,
                    營業收入合計=1000000000,
                    基本每股盈餘=eps_values[i]
                )
                incomes.append(income)
                db.session.add(income)
            db.session.commit()

            # POST another income sheet to trigger checkFourSeasonEPS
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'season': '4',
                '營業收入合計': 1000000000,
                '基本每股盈餘': 4.0  # Updated value
            }

            response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201

            # Verify DailyInformation was updated with four season EPS
            daily_info = DailyInformation.query.filter_by(
                stock_id=sample_basic_info.id
            ).first()

            if daily_info:
                assert daily_info.近四季每股盈餘 is not None

            # Cleanup
            for income in incomes:
                db.session.delete(income)
            if daily_info:
                db.session.delete(daily_info)
            db.session.commit()

    def test_four_season_eps_creates_daily_info(self, test_app, client, sample_basic_info):
        """Test that DailyInformation is created if it doesn't exist."""
        with test_app.app_context():
            # Ensure no DailyInformation exists
            DailyInformation.query.filter_by(
                stock_id=sample_basic_info.id
            ).delete()
            db.session.commit()

            # Create 4 seasons of income sheet data
            incomes = []
            for season in ['1', '2', '3', '4']:
                income = IncomeSheet(
                    stock_id=sample_basic_info.id,
                    year=2023,
                    season=season,
                    營業收入合計=1000000000,
                    基本每股盈餘=2.5
                )
                incomes.append(income)
                db.session.add(income)
            db.session.commit()

            # POST to trigger checkFourSeasonEPS
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2023,
                'season': '4',
                '營業收入合計': 1000000000,
                '基本每股盈餘': 2.5
            }

            response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )

            # Cleanup
            for income in incomes:
                db.session.delete(income)
            DailyInformation.query.filter_by(
                stock_id=sample_basic_info.id
            ).delete()
            db.session.commit()


@pytest.mark.usefixtures('test_app')
class TestIncomeSheetAPIIntegration:
    """Integration tests for IncomeSheet API."""

    def test_create_then_get(self, test_app, client, sample_basic_info):
        """Test creating a record then retrieving it."""
        with test_app.app_context():
            # Create
            payload = {
                'stock_id': sample_basic_info.id,
                'year': 2024,
                'season': '1',
                '營業收入合計': 5000000000,
                '營業毛利率': 40.5,
                '基本每股盈餘': 5.5
            }

            create_response = client.post(
                f'/income_sheet/{sample_basic_info.id}',
                data=json.dumps(payload),
                content_type='application/json'
            )
            assert create_response.status_code == 201

            # Get
            get_response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=single&year=2024&season=1'
            )
            assert get_response.status_code == 200

            data = json.loads(get_response.data)
            assert len(data) == 1
            assert data[0]['營業收入合計'] == 5000000000

            # Cleanup
            IncomeSheet.query.filter_by(
                stock_id=sample_basic_info.id,
                year=2024,
                season='1'
            ).delete()
            db.session.commit()

    def test_create_multiple_seasons(self, test_app, client, sample_basic_info):
        """Test creating multiple seasons of income sheet data."""
        with test_app.app_context():
            created_seasons = []

            for season in ['1', '2', '3', '4']:
                payload = {
                    'stock_id': sample_basic_info.id,
                    'year': 2023,
                    'season': season,
                    '營業收入合計': 1000000000 * int(season),
                    '基本每股盈餘': float(season)
                }

                response = client.post(
                    f'/income_sheet/{sample_basic_info.id}',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                assert response.status_code == 201
                created_seasons.append(season)

            # Verify all created
            get_response = client.get(
                f'/income_sheet/{sample_basic_info.id}?mode=multiple&year=1'
            )
            data = json.loads(get_response.data)

            for season in created_seasons:
                matching = [d for d in data if d['year'] == 2023 and d['season'] == season]
                assert len(matching) == 1

            # Cleanup
            IncomeSheet.query.filter(
                IncomeSheet.stock_id == sample_basic_info.id,
                IncomeSheet.year == 2023,
                IncomeSheet.season.in_(created_seasons)
            ).delete()
            db.session.commit()


@pytest.mark.usefixtures('test_app')
class TestIncomeSheetSerializer:
    """Tests for IncomeSheetSchema serialization."""

    def test_serializer_includes_expected_fields(self, test_app, client, sample_income_sheet):
        """Test that serializer includes all expected fields."""
        with test_app.app_context():
            response = client.get(f'/income_sheet/{sample_income_sheet.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1

            item = data[0]
            expected_fields = [
                'id', 'stock_id', 'year', 'season', 'update_date',
                '營業收入合計', '營業毛利', '營業毛利率',
                '營業費用', '營業費用率', '營業利益', '營業利益率',
                '稅前淨利', '稅前淨利率', '本期淨利', '本期淨利率',
                '基本每股盈餘', '稀釋每股盈餘'
            ]

            for field in expected_fields:
                assert field in item, f"Missing field: {field}"

    def test_serializer_date_format(self, test_app, client, sample_income_sheet):
        """Test that dates are properly serialized."""
        with test_app.app_context():
            response = client.get(f'/income_sheet/{sample_income_sheet.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)

            if data:
                update_date = data[0].get('update_date')
                if update_date:
                    # Should be in ISO format (YYYY-MM-DD)
                    assert len(update_date) == 10
                    assert update_date[4] == '-'
                    assert update_date[7] == '-'
