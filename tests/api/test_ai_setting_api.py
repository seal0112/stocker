"""Tests for GET/PUT /api/v0/ai_setting"""
import json
import pytest

from app import db
from app.ai_setting.models import AiSetting


@pytest.fixture(autouse=True)
def reset_ai_setting(test_app):
    """Ensure ai_setting table has exactly one row with known state before each test."""
    with test_app.app_context():
        AiSetting.query.delete()
        db.session.add(AiSetting(provider='gemini', model=None, updated_by='system'))
        db.session.commit()
    yield
    with test_app.app_context():
        AiSetting.query.delete()
        db.session.commit()


class TestAiSettingGet:

    def test_get_unauthenticated_401(self, test_app, client):
        response = client.get('/api/v0/ai_setting')
        assert response.status_code == 401

    def test_get_authenticated_200(self, test_app, authenticated_client):
        response = authenticated_client.get('/api/v0/ai_setting')
        assert response.status_code == 200
        data = response.get_json()
        assert data['provider'] == 'gemini'
        assert 'model' in data
        assert 'updated_by' in data
        assert 'updated_at' in data

    def test_get_creates_default_if_missing(self, test_app, authenticated_client):
        """Should auto-create default row if table is empty."""
        AiSetting.query.delete()
        db.session.commit()

        response = authenticated_client.get('/api/v0/ai_setting')
        assert response.status_code == 200
        data = response.get_json()
        assert data['provider'] == 'gemini'


class TestAiSettingPut:

    def test_put_unauthenticated_401(self, test_app, client):
        response = client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'claude'}),
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_put_regular_user_403(self, test_app, authenticated_client):
        response = authenticated_client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'claude'}),
            content_type='application/json'
        )
        assert response.status_code == 403

    def test_put_admin_switch_provider(self, test_app, admin_authenticated_client):
        response = admin_authenticated_client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'claude', 'model': 'claude-sonnet-4-6'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['provider'] == 'claude'
        assert data['model'] == 'claude-sonnet-4-6'

    def test_put_admin_switch_to_gemini(self, test_app, admin_authenticated_client):
        response = admin_authenticated_client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'gemini', 'model': 'gemini-2.0-flash'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['provider'] == 'gemini'
        assert data['model'] == 'gemini-2.0-flash'

    def test_put_null_model_allowed(self, test_app, admin_authenticated_client):
        """model=None should clear the model (use provider default)."""
        response = admin_authenticated_client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'gemini', 'model': None}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['model'] is None

    def test_put_invalid_provider_400(self, test_app, admin_authenticated_client):
        response = admin_authenticated_client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'openai'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'Invalid provider' in response.get_json()['error']

    def test_put_invalid_model_for_provider_400(self, test_app, admin_authenticated_client):
        """Gemini model name should not be accepted for claude provider."""
        response = admin_authenticated_client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'claude', 'model': 'gemini-2.5-flash-preview-05-20'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'Invalid model' in response.get_json()['error']

    def test_put_missing_body_400(self, test_app, admin_authenticated_client):
        response = admin_authenticated_client.put(
            '/api/v0/ai_setting',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_put_persists_to_db(self, test_app, admin_authenticated_client):
        """Change should be reflected in subsequent GET."""
        admin_authenticated_client.put(
            '/api/v0/ai_setting',
            data=json.dumps({'provider': 'claude', 'model': 'claude-opus-4-7'}),
            content_type='application/json'
        )
        setting = AiSetting.query.first()
        assert setting.provider == 'claude'
        assert setting.model == 'claude-opus-4-7'
