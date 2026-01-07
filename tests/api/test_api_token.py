"""API tests for API token endpoints."""
import pytest
import json
from unittest.mock import patch

from app import db
from app.models import ApiToken


@pytest.fixture
def auth_headers(regular_user):
    """Create mock JWT auth headers."""
    return {
        'user_identity': {
            'id': regular_user.id,
            'username': regular_user.username,
            'email': regular_user.email,
            'picture': None
        }
    }


class TestApiTokenListEndpoint:
    """Tests for GET/POST /api/v1/token."""

    def test_list_tokens_empty(self, client, regular_user, auth_headers):
        """Should return empty list when no tokens exist."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.get('/api/v1/token')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data == []

    def test_create_token_success(self, client, regular_user, auth_headers):
        """Should create a new token successfully."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.post(
                    '/api/v1/token',
                    data=json.dumps({'name': 'My API Token'}),
                    content_type='application/json'
                )
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['name'] == 'My API Token'
                assert 'token' in data  # Plain token should be returned
                assert data['token'].startswith('stk_')
                assert data['is_active'] is True

    def test_create_token_with_scopes(self, client, regular_user, auth_headers):
        """Should create a token with scopes."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.post(
                    '/api/v1/token',
                    data=json.dumps({
                        'name': 'Scoped Token',
                        'scopes': ['read', 'write']
                    }),
                    content_type='application/json'
                )
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['scopes'] == ['read', 'write']

    def test_create_token_with_expiration(self, client, regular_user, auth_headers):
        """Should create a token with expiration."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.post(
                    '/api/v1/token',
                    data=json.dumps({
                        'name': 'Expiring Token',
                        'expires_in_days': 30
                    }),
                    content_type='application/json'
                )
                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['expires_at'] is not None

    def test_create_token_missing_name(self, client, regular_user, auth_headers):
        """Should return 400 when name is missing."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.post(
                    '/api/v1/token',
                    data=json.dumps({}),
                    content_type='application/json'
                )
                assert response.status_code == 400

    def test_create_token_exceeds_limit(self, client, regular_user, auth_headers):
        """Should return 400 when token limit is exceeded."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                # Create max tokens
                for i in range(ApiToken.MAX_TOKENS_PER_USER):
                    client.post(
                        '/api/v1/token',
                        data=json.dumps({'name': f'Token {i}'}),
                        content_type='application/json'
                    )

                # Try to create one more
                response = client.post(
                    '/api/v1/token',
                    data=json.dumps({'name': 'Extra Token'}),
                    content_type='application/json'
                )
                assert response.status_code == 400
                data = json.loads(response.data)
                assert 'Maximum' in data['error']

    def test_list_tokens_returns_created_tokens(self, client, regular_user, auth_headers):
        """Should return all created tokens."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                # Create tokens
                client.post(
                    '/api/v1/token',
                    data=json.dumps({'name': 'Token 1'}),
                    content_type='application/json'
                )
                client.post(
                    '/api/v1/token',
                    data=json.dumps({'name': 'Token 2'}),
                    content_type='application/json'
                )

                # List tokens
                response = client.get('/api/v1/token')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert len(data) == 2
                # Plain token should NOT be returned in list
                assert 'token' not in data[0] or data[0]['token'] is None


class TestApiTokenDetailEndpoint:
    """Tests for GET/DELETE /api/v1/token/<id>."""

    def test_get_token_success(self, client, regular_user, auth_headers):
        """Should return token details."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                # Create a token
                create_response = client.post(
                    '/api/v1/token',
                    data=json.dumps({'name': 'Detail Token'}),
                    content_type='application/json'
                )
                created = json.loads(create_response.data)
                token_id = created['id']

                # Get token
                response = client.get(f'/api/v1/token/{token_id}')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['id'] == token_id
                assert data['name'] == 'Detail Token'

    def test_get_token_not_found(self, client, regular_user, auth_headers):
        """Should return 404 for non-existent token."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.get('/api/v1/token/nonexistent-id')
                assert response.status_code == 404

    def test_delete_token_success(self, client, regular_user, auth_headers):
        """Should delete (revoke) token successfully."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                # Create a token
                create_response = client.post(
                    '/api/v1/token',
                    data=json.dumps({'name': 'Delete Token'}),
                    content_type='application/json'
                )
                created = json.loads(create_response.data)
                token_id = created['id']

                # Delete token
                response = client.delete(f'/api/v1/token/{token_id}')
                assert response.status_code == 204

                # Verify token is gone from list
                list_response = client.get('/api/v1/token')
                tokens = json.loads(list_response.data)
                assert all(t['id'] != token_id for t in tokens)

    def test_delete_token_not_found(self, client, regular_user, auth_headers):
        """Should return 404 for non-existent token."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.delete('/api/v1/token/nonexistent-id')
                assert response.status_code == 404


class TestApiTokenRegenerateEndpoint:
    """Tests for POST /api/v1/token/<id>/regenerate."""

    def test_regenerate_token_success(self, client, regular_user, auth_headers):
        """Should regenerate token with new value."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                # Create a token
                create_response = client.post(
                    '/api/v1/token',
                    data=json.dumps({'name': 'Regenerate Token'}),
                    content_type='application/json'
                )
                created = json.loads(create_response.data)
                token_id = created['id']
                old_token = created['token']

                # Regenerate token
                response = client.post(f'/api/v1/token/{token_id}/regenerate')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'token' in data
                assert data['token'] != old_token
                assert data['token'].startswith('stk_')

    def test_regenerate_token_not_found(self, client, regular_user, auth_headers):
        """Should return 404 for non-existent token."""
        with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
            with patch('flask_jwt_extended.get_jwt_identity', return_value=auth_headers['user_identity']):
                response = client.post('/api/v1/token/nonexistent-id/regenerate')
                assert response.status_code == 404
