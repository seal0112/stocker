"""Tests for Auth API endpoints."""
import pytest
from flask_jwt_extended import create_access_token

from app import db
from app.models.user import User
from app.models.role import Role


@pytest.fixture
def get_auth_client(client):
    def _auth_client(user):
        identity = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'picture': user.profile_pic
        }
        token = create_access_token(identity=identity)
        client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return client
    return _auth_client


class TestGetUserInfo:
    """Tests for GET /api/auth/user_info endpoint."""

    def test_get_user_info_with_valid_token(self, test_app, get_auth_client, regular_user):
        """Should return user info with roles when authenticated."""
        auth_client = get_auth_client(regular_user)
        response = auth_client.get('/api/auth/user_info')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == regular_user.id
        assert data['username'] == regular_user.username
        assert data['email'] == regular_user.email
        assert 'roles' in data
        assert 'user' in data['roles']

    def test_get_user_info_without_token(self, test_app, client):
        """Should return 401 when no token provided."""
        response = client.get('/api/auth/user_info')

        assert response.status_code == 401

    def test_get_user_info_with_invalid_token(self, test_app, client):
        """Should return 401/422 when invalid token provided."""
        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': 'Bearer invalid_token_here'}
        )

        assert response.status_code in [401, 422]

    def test_get_user_info_admin_user(self, test_app, get_auth_client, admin_user):
        """Should return admin role in roles list."""
        auth_client = get_auth_client(admin_user)
        response = auth_client.get(
            '/api/auth/user_info'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'admin' in data['roles']

    def test_get_user_info_moderator_user(self, test_app, get_auth_client, moderator_user):
        """Should return moderator role in roles list."""
        auth_client = get_auth_client(moderator_user)
        response = auth_client.get('/api/auth/user_info')

        assert response.status_code == 200
        data = response.get_json()
        assert 'moderator' in data['roles']

    def test_get_user_info_user_with_multiple_roles(
        self, test_app, get_auth_client, multi_role_user
    ):
        """Should return all roles for user with multiple roles."""
        auth_client = get_auth_client(multi_role_user)
        response = auth_client.get('/api/auth/user_info')

        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data['roles']
        assert 'admin' in data['roles']
        assert 'moderator' in data['roles']
        assert len(data['roles']) == 3

    def test_get_user_info_user_no_roles(self, test_app, get_auth_client, user_no_roles):
        """Should return empty roles list for user without roles."""
        auth_client = get_auth_client(user_no_roles)
        response = auth_client.get('/api/auth/user_info')

        assert response.status_code == 200
        data = response.get_json()
        assert data['roles'] == []

    def test_get_user_info_deleted_user(self, test_app, client, deleted_user_token):
        """Should return empty roles when user no longer exists."""
        # Try to get user info with valid token but deleted user
        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {deleted_user_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        # User not found, should return empty roles
        assert data['roles'] == []

    def test_get_user_info_returns_identity_fields(self, test_app, get_auth_client, regular_user):
        """Should return all identity fields from JWT."""
        auth_client = get_auth_client(regular_user)
        response = auth_client.get('/api/auth/user_info')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == regular_user.id
        assert data['username'] == regular_user.username
        assert data['email'] == regular_user.email
        assert data['picture'] == regular_user.profile_pic