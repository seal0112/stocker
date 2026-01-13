"""API tests for API token endpoints."""
import pytest
import json

from app import db
from app.models import ApiToken


class TestApiTokenListEndpoint:
    """Tests for GET/POST /api/v1/token."""

    def test_list_tokens_empty(self, test_app, moderator_authenticated_client, moderator_user):
        """Should return empty list when no tokens exist."""
        # Clean up any existing tokens for this user
        ApiToken.query.filter_by(user_id=moderator_user.id).delete()
        db.session.commit()

        response = moderator_authenticated_client.get('/api/v1/token')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_create_token_success(self, test_app, moderator_authenticated_client, moderator_user):
        """Should create a new token successfully."""
        response = moderator_authenticated_client.post(
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

        # Cleanup
        ApiToken.query.filter_by(id=data['id']).delete()
        db.session.commit()

    def test_create_token_with_scopes(self, test_app, moderator_authenticated_client, moderator_user):
        """Should create a token with scopes."""
        response = moderator_authenticated_client.post(
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

        # Cleanup
        ApiToken.query.filter_by(id=data['id']).delete()
        db.session.commit()

    def test_create_token_with_expiration(self, test_app, moderator_authenticated_client, moderator_user):
        """Should create a token with expiration."""
        response = moderator_authenticated_client.post(
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

        # Cleanup
        ApiToken.query.filter_by(id=data['id']).delete()
        db.session.commit()

    def test_create_token_missing_name(self, test_app, moderator_authenticated_client):
        """Should return 400 when name is missing."""
        response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_create_token_exceeds_limit(self, test_app, moderator_authenticated_client, moderator_user):
        """Should return 400 when token limit is exceeded."""
        # Clean up first
        ApiToken.query.filter_by(user_id=moderator_user.id).delete()
        db.session.commit()

        # Create max tokens
        created_ids = []
        for i in range(ApiToken.MAX_TOKENS_PER_USER):
            response = moderator_authenticated_client.post(
                '/api/v1/token',
                data=json.dumps({'name': f'Token {i}'}),
                content_type='application/json'
            )
            if response.status_code == 201:
                data = json.loads(response.data)
                created_ids.append(data['id'])

        # Try to create one more
        response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Extra Token'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Maximum' in data['error']

        # Cleanup
        for token_id in created_ids:
            ApiToken.query.filter_by(id=token_id).delete()
        db.session.commit()

    def test_list_tokens_returns_created_tokens(self, test_app, moderator_authenticated_client, moderator_user):
        """Should return all created tokens."""
        # Clean up first
        ApiToken.query.filter_by(user_id=moderator_user.id).delete()
        db.session.commit()

        # Create tokens
        response1 = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Token 1'}),
            content_type='application/json'
        )
        response2 = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Token 2'}),
            content_type='application/json'
        )

        # List tokens
        response = moderator_authenticated_client.get('/api/v1/token')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        # Plain token should NOT be returned in list
        assert 'token' not in data[0] or data[0]['token'] is None

        # Cleanup
        ApiToken.query.filter_by(user_id=moderator_user.id).delete()
        db.session.commit()


class TestApiTokenDetailEndpoint:
    """Tests for GET/DELETE /api/v1/token/<id>."""

    def test_get_token_success(self, test_app, moderator_authenticated_client, moderator_user):
        """Should return token details."""
        # Create a token
        create_response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Detail Token'}),
            content_type='application/json'
        )
        created = json.loads(create_response.data)
        token_id = created['id']

        # Get token
        response = moderator_authenticated_client.get(f'/api/v1/token/{token_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == token_id
        assert data['name'] == 'Detail Token'

        # Cleanup
        ApiToken.query.filter_by(id=token_id).delete()
        db.session.commit()

    def test_get_token_not_found(self, test_app, moderator_authenticated_client):
        """Should return 404 for non-existent token."""
        response = moderator_authenticated_client.get('/api/v1/token/nonexistent-id')
        assert response.status_code == 404

    def test_delete_token_success(self, test_app, moderator_authenticated_client, moderator_user):
        """Should delete (revoke) token successfully."""
        # Create a token
        create_response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Delete Token'}),
            content_type='application/json'
        )
        created = json.loads(create_response.data)
        token_id = created['id']

        # Delete token
        response = moderator_authenticated_client.delete(f'/api/v1/token/{token_id}')
        assert response.status_code == 204

        # Verify token is gone from list
        list_response = moderator_authenticated_client.get('/api/v1/token')
        tokens = json.loads(list_response.data)
        assert all(t['id'] != token_id for t in tokens)

    def test_delete_token_not_found(self, test_app, moderator_authenticated_client):
        """Should return 404 for non-existent token."""
        response = moderator_authenticated_client.delete('/api/v1/token/nonexistent-id')
        assert response.status_code == 404


class TestApiTokenRegenerateEndpoint:
    """Tests for POST /api/v1/token/<id>/regenerate."""

    def test_regenerate_token_success(self, test_app, moderator_authenticated_client, moderator_user):
        """Should regenerate token with new value."""
        # Create a token
        create_response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Regenerate Token'}),
            content_type='application/json'
        )
        created = json.loads(create_response.data)
        token_id = created['id']
        old_token = created['token']

        # Regenerate token
        response = moderator_authenticated_client.post(f'/api/v1/token/{token_id}/regenerate')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert data['token'] != old_token
        assert data['token'].startswith('stk_')

        # Cleanup
        ApiToken.query.filter_by(id=token_id).delete()
        db.session.commit()

    def test_regenerate_token_not_found(self, test_app, moderator_authenticated_client):
        """Should return 404 for non-existent token."""
        response = moderator_authenticated_client.post('/api/v1/token/nonexistent-id/regenerate')
        assert response.status_code == 404
