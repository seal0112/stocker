"""API tests for API token endpoints."""
import pytest
import json
from datetime import datetime, timedelta, timezone

from app import db
from app.models import ApiToken


# ============================================================================
# Yield-based fixtures for automatic cleanup
# ============================================================================

@pytest.fixture
def token_factory(moderator_user):
    """Factory fixture to create tokens with automatic cleanup."""
    created_ids = []

    def _create_token(name="Test Token", scopes=None, expires_in_days=None):
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        token, _ = ApiToken.create_token(
            user_id=moderator_user.id,
            name=name,
            scopes=scopes,
            expires_at=expires_at
        )
        created_ids.append(token.id)
        return token

    yield _create_token

    # Cleanup all created tokens
    if created_ids:
        ApiToken.query.filter(ApiToken.id.in_(created_ids)).delete(synchronize_session=False)
        db.session.commit()


@pytest.fixture
def clean_user_tokens(moderator_user):
    """Ensure user has no tokens before and after test."""
    ApiToken.query.filter_by(user_id=moderator_user.id).delete()
    db.session.commit()

    yield

    ApiToken.query.filter_by(user_id=moderator_user.id).delete()
    db.session.commit()


@pytest.fixture
def other_user_token(regular_user):
    """Create a token for another user (for cross-user access tests)."""
    token, _ = ApiToken.create_token(
        user_id=regular_user.id,
        name="Other User Token",
        scopes=[]
    )

    yield token

    ApiToken.query.filter_by(id=token.id).delete()
    db.session.commit()


# ============================================================================
# Test Classes
# ============================================================================

@pytest.mark.usefixtures('test_app')
class TestApiTokenListEndpoint:
    """Tests for GET/POST /api/v1/token."""

    def test_list_tokens_empty(self, moderator_authenticated_client, clean_user_tokens):
        """Should return empty list when no tokens exist."""
        response = moderator_authenticated_client.get('/api/v1/token')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_create_token_success(self, moderator_authenticated_client, token_factory):
        """Should create a new token successfully."""
        response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'My API Token'}),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'My API Token'
        assert 'token' in data
        assert data['token'].startswith('stk_')
        assert data['is_active'] is True

    def test_create_token_with_scopes(self, moderator_authenticated_client, token_factory):
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

    def test_create_token_with_expiration(self, moderator_authenticated_client, token_factory):
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

    def test_create_token_missing_name(self, moderator_authenticated_client):
        """Should return 400 when name is missing."""
        response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_create_token_exceeds_limit(self, moderator_authenticated_client, clean_user_tokens):
        """Should return 400 when token limit is exceeded."""
        # Create max tokens
        for i in range(ApiToken.MAX_TOKENS_PER_USER):
            moderator_authenticated_client.post(
                '/api/v1/token',
                data=json.dumps({'name': f'Token {i}'}),
                content_type='application/json'
            )

        # Try to create one more
        response = moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Extra Token'}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Maximum' in data['error']

    def test_list_tokens_returns_created_tokens(self, moderator_authenticated_client, token_factory, clean_user_tokens):
        """Should return all created tokens."""
        # Create tokens via API
        moderator_authenticated_client.post(
            '/api/v1/token',
            data=json.dumps({'name': 'Token 1'}),
            content_type='application/json'
        )
        moderator_authenticated_client.post(
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

    def test_list_tokens_only_returns_own_tokens(self, moderator_authenticated_client, token_factory, other_user_token):
        """Should only return tokens belonging to the authenticated user."""
        # Create a token for moderator
        token_factory(name="Moderator Token")

        response = moderator_authenticated_client.get('/api/v1/token')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should not include other user's token
        token_ids = [t['id'] for t in data]
        assert other_user_token.id not in token_ids


@pytest.mark.usefixtures('test_app')
class TestApiTokenDetailEndpoint:
    """Tests for GET/DELETE /api/v1/token/<id>."""

    def test_get_token_success(self, moderator_authenticated_client, token_factory):
        """Should return token details."""
        token = token_factory(name="Detail Token")

        response = moderator_authenticated_client.get(f'/api/v1/token/{token.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == token.id
        assert data['name'] == 'Detail Token'
        # Plain token should NOT be returned in detail
        assert 'token' not in data or data['token'] is None

    def test_get_token_not_found(self, moderator_authenticated_client):
        """Should return 404 for non-existent token."""
        response = moderator_authenticated_client.get('/api/v1/token/nonexistent-id')

        assert response.status_code == 404

    def test_get_other_user_token_returns_404(self, moderator_authenticated_client, other_user_token):
        """Should return 404 when trying to access another user's token."""
        response = moderator_authenticated_client.get(f'/api/v1/token/{other_user_token.id}')

        # Should return 404 (not 403) to avoid leaking information
        assert response.status_code == 404

    def test_delete_token_success(self, moderator_authenticated_client, token_factory):
        """Should delete (revoke) token successfully."""
        token = token_factory(name="Delete Token")
        token_id = token.id

        response = moderator_authenticated_client.delete(f'/api/v1/token/{token_id}')

        assert response.status_code == 204

        # Verify token is gone
        list_response = moderator_authenticated_client.get('/api/v1/token')
        tokens = json.loads(list_response.data)
        assert all(t['id'] != token_id for t in tokens)

    def test_delete_token_not_found(self, moderator_authenticated_client):
        """Should return 404 for non-existent token."""
        response = moderator_authenticated_client.delete('/api/v1/token/nonexistent-id')

        assert response.status_code == 404

    def test_delete_other_user_token_returns_404(self, moderator_authenticated_client, other_user_token):
        """Should return 404 when trying to delete another user's token."""
        response = moderator_authenticated_client.delete(f'/api/v1/token/{other_user_token.id}')

        # Should return 404 to avoid leaking information
        assert response.status_code == 404

        # Verify token still exists
        token = ApiToken.query.filter_by(id=other_user_token.id).first()
        assert token is not None


@pytest.mark.usefixtures('test_app')
class TestApiTokenRegenerateEndpoint:
    """Tests for POST /api/v1/token/<id>/regenerate."""

    def test_regenerate_token_success(self, moderator_authenticated_client, token_factory):
        """Should regenerate token with new value."""
        token = token_factory(name="Regenerate Token")
        old_token_hash = token.token_hash

        response = moderator_authenticated_client.post(f'/api/v1/token/{token.id}/regenerate')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert data['token'].startswith('stk_')

        # Verify hash changed in database
        db.session.refresh(token)
        assert token.token_hash != old_token_hash

    def test_regenerate_token_not_found(self, moderator_authenticated_client):
        """Should return 404 for non-existent token."""
        response = moderator_authenticated_client.post('/api/v1/token/nonexistent-id/regenerate')

        assert response.status_code == 404

    def test_regenerate_other_user_token_returns_404(self, moderator_authenticated_client, other_user_token):
        """Should return 404 when trying to regenerate another user's token."""
        old_hash = other_user_token.token_hash

        response = moderator_authenticated_client.post(f'/api/v1/token/{other_user_token.id}/regenerate')

        assert response.status_code == 404

        # Verify token was not regenerated
        db.session.refresh(other_user_token)
        assert other_user_token.token_hash == old_hash


@pytest.mark.usefixtures('test_app')
class TestApiTokenSecurity:
    """Security-focused tests for API token endpoints."""

    def test_expired_token_marked_inactive(self, moderator_authenticated_client, moderator_user):
        """Should mark expired tokens correctly."""
        # Create an expired token directly in DB
        plain_token = ApiToken.generate_token()
        token = ApiToken(
            user_id=moderator_user.id,
            name="Expired Token",
            token_hash=ApiToken.hash_token(plain_token),
            token_prefix=ApiToken.get_token_prefix(plain_token),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.session.add(token)
        db.session.commit()

        response = moderator_authenticated_client.get(f'/api/v1/token/{token.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        # Token should be marked as expired/inactive
        assert data['is_active'] is False or data.get('is_expired') is True

        # Cleanup
        db.session.delete(token)
        db.session.commit()

    def test_token_not_exposed_in_list(self, moderator_authenticated_client, token_factory):
        """Plain token value should never be exposed in list endpoint."""
        token_factory(name="Secret Token")

        response = moderator_authenticated_client.get('/api/v1/token')

        assert response.status_code == 200
        data = json.loads(response.data)
        for item in data:
            # token field should either not exist or be None/masked
            if 'token' in item:
                assert item['token'] is None or item['token'] == ''

    def test_token_not_exposed_in_detail(self, moderator_authenticated_client, token_factory):
        """Plain token value should never be exposed in detail endpoint."""
        token = token_factory(name="Secret Token")

        response = moderator_authenticated_client.get(f'/api/v1/token/{token.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        # token field should either not exist or be None/masked
        if 'token' in data:
            assert data['token'] is None or data['token'] == ''
