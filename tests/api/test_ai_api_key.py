"""Tests for /api/v0/ai_api_key endpoints."""
import json
from unittest.mock import patch, MagicMock
import pytest

from app import db
from app.ai_api_key.models import AiApiKey


@pytest.fixture(autouse=True)
def clean_ai_api_key(test_app):
    with test_app.app_context():
        AiApiKey.query.delete()
        db.session.commit()
    yield
    with test_app.app_context():
        AiApiKey.query.delete()
        db.session.commit()


@pytest.fixture
def sample_key(test_app):
    with test_app.app_context():
        key = AiApiKey(
            name='test-gemini-key',
            provider='gemini',
            owner='User A',
            ssm_path='/stocker/ai_key/test-gemini-key',
            is_active=True,
        )
        db.session.add(key)
        db.session.commit()
        yield key.id


class TestListKeys:

    def test_unauthenticated_401(self, client):
        assert client.get('/api/v0/ai_api_key').status_code == 401

    def test_regular_user_403(self, authenticated_client):
        assert authenticated_client.get('/api/v0/ai_api_key').status_code == 403

    def test_admin_returns_list(self, admin_authenticated_client, sample_key):
        resp = admin_authenticated_client.get('/api/v0/ai_api_key')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['name'] == 'test-gemini-key'
        assert 'ssm_path' in data[0]


class TestCreateKey:

    @patch('app.ai_api_key.views._ssm_client')
    def test_create_success(self, mock_ssm_cls, admin_authenticated_client):
        mock_ssm = MagicMock()
        mock_ssm_cls.return_value = mock_ssm

        resp = admin_authenticated_client.post(
            '/api/v0/ai_api_key',
            data=json.dumps({
                'name': 'userb-gemini',
                'provider': 'gemini',
                'owner': 'User B',
                'key_value': 'AIza-fake-key',
            }),
            content_type='application/json',
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['name'] == 'userb-gemini'
        assert data['ssm_path'] == '/stocker/ai_key/userb-gemini'
        mock_ssm.put_parameter.assert_called_once()

    def test_missing_required_fields_400(self, admin_authenticated_client):
        resp = admin_authenticated_client.post(
            '/api/v0/ai_api_key',
            data=json.dumps({'name': 'only-name'}),
            content_type='application/json',
        )
        assert resp.status_code == 400

    @patch('app.ai_api_key.views._ssm_client')
    def test_duplicate_name_409(self, mock_ssm_cls, admin_authenticated_client, sample_key):
        mock_ssm_cls.return_value = MagicMock()
        resp = admin_authenticated_client.post(
            '/api/v0/ai_api_key',
            data=json.dumps({
                'name': 'test-gemini-key',
                'provider': 'gemini',
                'key_value': 'some-key',
            }),
            content_type='application/json',
        )
        assert resp.status_code == 409

    def test_unauthenticated_401(self, client):
        assert client.post('/api/v0/ai_api_key').status_code == 401

    def test_regular_user_403(self, authenticated_client):
        resp = authenticated_client.post(
            '/api/v0/ai_api_key',
            data=json.dumps({'name': 'x', 'provider': 'gemini', 'key_value': 'y'}),
            content_type='application/json',
        )
        assert resp.status_code == 403


class TestUpdateKey:

    @patch('app.ai_api_key.views._ssm_client')
    def test_update_key_value(self, mock_ssm_cls, admin_authenticated_client, sample_key):
        mock_ssm = MagicMock()
        mock_ssm_cls.return_value = mock_ssm

        resp = admin_authenticated_client.put(
            f'/api/v0/ai_api_key/{sample_key}',
            data=json.dumps({'key_value': 'new-api-key', 'owner': 'User C'}),
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.get_json()['owner'] == 'User C'
        mock_ssm.put_parameter.assert_called_once()

    @patch('app.ai_api_key.views._ssm_client')
    def test_update_without_key_value_no_ssm_call(self, mock_ssm_cls, admin_authenticated_client, sample_key):
        mock_ssm = MagicMock()
        mock_ssm_cls.return_value = mock_ssm

        resp = admin_authenticated_client.put(
            f'/api/v0/ai_api_key/{sample_key}',
            data=json.dumps({'is_active': False}),
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.get_json()['is_active'] is False
        mock_ssm.put_parameter.assert_not_called()

    def test_not_found_404(self, admin_authenticated_client):
        resp = admin_authenticated_client.put(
            '/api/v0/ai_api_key/99999',
            data=json.dumps({'owner': 'x'}),
            content_type='application/json',
        )
        assert resp.status_code == 404


class TestDeleteKey:

    @patch('app.ai_api_key.views._ssm_client')
    def test_delete_success(self, mock_ssm_cls, admin_authenticated_client, sample_key):
        mock_ssm = MagicMock()
        mock_ssm_cls.return_value = mock_ssm

        resp = admin_authenticated_client.delete(f'/api/v0/ai_api_key/{sample_key}')
        assert resp.status_code == 200
        mock_ssm.delete_parameter.assert_called_once()

        resp2 = admin_authenticated_client.get('/api/v0/ai_api_key')
        assert resp2.get_json() == []

    def test_not_found_404(self, admin_authenticated_client):
        assert admin_authenticated_client.delete('/api/v0/ai_api_key/99999').status_code == 404

    def test_unauthenticated_401(self, client):
        assert client.delete('/api/v0/ai_api_key/1').status_code == 401
