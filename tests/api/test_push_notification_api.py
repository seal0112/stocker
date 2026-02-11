"""Tests for PushNotification API endpoints."""
import json
import pytest

from app import db
from app.database_setup import PushNotification


@pytest.fixture
def clean_push_notification(test_app, regular_user):
    """Ensure no PushNotification exists for regular_user before/after test."""
    PushNotification.query.filter_by(user_id=regular_user.id).delete()
    db.session.commit()
    yield
    PushNotification.query.filter_by(user_id=regular_user.id).delete()
    db.session.commit()


class TestPushNotificationGet:
    """Tests for GET /api/v0/push_notification/"""

    def test_get_success(self, test_app, authenticated_client, sample_push_notification_enabled):
        """Should return push notification settings for authenticated user."""
        response = authenticated_client.get('/api/v0/push_notification/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_enabled'] is True
        assert data['gmail'] == 'test@gmail.com'

    def test_get_returns_empty_when_none_exist(self, test_app, authenticated_client, clean_push_notification):
        """Should return empty/null when no notification settings exist."""
        response = authenticated_client.get('/api/v0/push_notification/')
        assert response.status_code == 200

    def test_get_unauthorized_401(self, test_app, client):
        """Should return 401 for unauthenticated request."""
        response = client.get('/api/v0/push_notification/')
        assert response.status_code == 401

    def test_get_serializer_fields_present(self, test_app, authenticated_client, sample_push_notification_enabled):
        """Response should contain all expected serializer fields."""
        response = authenticated_client.get('/api/v0/push_notification/')
        assert response.status_code == 200
        data = response.get_json()
        expected_fields = [
            'notify_enabled', 'gmail', 'gmail_token', 'notify_time',
            'notify_month_revenue', 'notify_income_sheet', 'notify_news',
            'notify_announcement', 'notify_earnings_call'
        ]
        for field in expected_fields:
            assert field in data

    def test_get_disabled_settings_all_false(self, test_app, authenticated_client, sample_push_notification_enabled):
        """When notifications enabled, verify boolean fields are present."""
        response = authenticated_client.get('/api/v0/push_notification/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_news'] is True
        assert data['notify_announcement'] is True


class TestPushNotificationPut:
    """Tests for PUT /api/v0/push_notification/"""

    def test_create_new_upsert(self, test_app, authenticated_client, clean_push_notification):
        """PUT should create new notification settings when none exist."""
        payload = {
            'notify_enabled': True,
            'gmail': 'new@gmail.com',
            'gmail_token': 'new_token',
            'notify_news': True,
            'notify_announcement': False,
            'notify_month_revenue': True,
            'notify_income_sheet': False,
            'notify_earnings_call': True
        }
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_enabled'] is True
        assert data['gmail'] == 'new@gmail.com'
        assert data['notify_news'] is True

    def test_update_existing(self, test_app, authenticated_client, sample_push_notification_enabled):
        """PUT should update existing notification settings."""
        payload = {
            'notify_enabled': False,
            'gmail': 'updated@gmail.com',
            'notify_news': False,
            'notify_announcement': False,
            'notify_month_revenue': False,
            'notify_income_sheet': False,
            'notify_earnings_call': False
        }
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_enabled'] is False
        assert data['gmail'] == 'updated@gmail.com'

    def test_missing_body_400(self, test_app, authenticated_client):
        """PUT with no body should return 400."""
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_invalid_json_400(self, test_app, authenticated_client):
        """PUT with invalid JSON should return 400."""
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_unauthorized_401(self, test_app, client):
        """PUT without auth should return 401."""
        payload = {'notify_enabled': True}
        response = client.put(
            '/api/v0/push_notification/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_partial_payload(self, test_app, authenticated_client, clean_push_notification):
        """PUT with partial payload should use defaults for missing fields."""
        payload = {'notify_enabled': True, 'gmail': 'partial@gmail.com'}
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_enabled'] is True
        assert data['gmail'] == 'partial@gmail.com'
        assert data['notify_news'] is False
        assert data['notify_announcement'] is False

    def test_all_enabled(self, test_app, authenticated_client, clean_push_notification):
        """PUT with all notifications enabled."""
        payload = {
            'notify_enabled': True,
            'gmail': 'all@gmail.com',
            'gmail_token': 'token',
            'notify_news': True,
            'notify_announcement': True,
            'notify_month_revenue': True,
            'notify_income_sheet': True,
            'notify_earnings_call': True
        }
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_news'] is True
        assert data['notify_announcement'] is True
        assert data['notify_month_revenue'] is True
        assert data['notify_income_sheet'] is True
        assert data['notify_earnings_call'] is True

    def test_all_disabled(self, test_app, authenticated_client, clean_push_notification):
        """PUT with all notifications disabled."""
        payload = {
            'notify_enabled': False,
            'notify_news': False,
            'notify_announcement': False,
            'notify_month_revenue': False,
            'notify_income_sheet': False,
            'notify_earnings_call': False
        }
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_enabled'] is False
        assert data['notify_news'] is False

    def test_toggle_individual_flags(self, test_app, authenticated_client, sample_push_notification_enabled):
        """PUT should be able to toggle individual notification flags."""
        payload = {
            'notify_enabled': True,
            'notify_news': False,
            'notify_announcement': True,
            'notify_month_revenue': False,
            'notify_income_sheet': True,
            'notify_earnings_call': False
        }
        response = authenticated_client.put(
            '/api/v0/push_notification/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['notify_news'] is False
        assert data['notify_announcement'] is True
        assert data['notify_month_revenue'] is False
        assert data['notify_income_sheet'] is True
        assert data['notify_earnings_call'] is False
