"""Tests for Auth API endpoints."""
import pytest
from flask_jwt_extended import create_access_token

from app import db
from app.models.user import User
from app.models.role import Role


class TestGetUserInfo:
    """Tests for GET /api/auth/user_info endpoint."""

    def test_get_user_info_with_valid_token(self, test_app, client, regular_user):
        """Should return user info with roles when authenticated."""
        identity = {
            'id': regular_user.id,
            'username': regular_user.username,
            'email': regular_user.email,
            'picture': regular_user.profile_pic
        }
        access_token = create_access_token(identity=identity)

        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {access_token}'}
        )

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

    def test_get_user_info_admin_user(self, test_app, client, admin_user):
        """Should return admin role in roles list."""
        identity = {
            'id': admin_user.id,
            'username': admin_user.username,
            'email': admin_user.email,
            'picture': admin_user.profile_pic
        }
        access_token = create_access_token(identity=identity)

        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'admin' in data['roles']

    def test_get_user_info_moderator_user(self, test_app, client, moderator_user):
        """Should return moderator role in roles list."""
        identity = {
            'id': moderator_user.id,
            'username': moderator_user.username,
            'email': moderator_user.email,
            'picture': moderator_user.profile_pic
        }
        access_token = create_access_token(identity=identity)

        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'moderator' in data['roles']

    def test_get_user_info_user_with_multiple_roles(
        self, test_app, client, user_role, admin_role, moderator_role
    ):
        """Should return all roles for user with multiple roles."""
        user = User(
            username='multi_role_user',
            email='multi_role@test.com',
            active=True,
            authenticate=True
        )
        user.set_password('testpassword123')
        user.roles.append(user_role)
        user.roles.append(admin_role)
        user.roles.append(moderator_role)
        db.session.add(user)
        db.session.commit()

        identity = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'picture': user.profile_pic
        }
        access_token = create_access_token(identity=identity)

        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data['roles']
        assert 'admin' in data['roles']
        assert 'moderator' in data['roles']
        assert len(data['roles']) == 3

        # Cleanup
        db.session.delete(user)
        db.session.commit()

    def test_get_user_info_user_no_roles(self, test_app, client, user_no_roles):
        """Should return empty roles list for user without roles."""
        identity = {
            'id': user_no_roles.id,
            'username': user_no_roles.username,
            'email': user_no_roles.email,
            'picture': user_no_roles.profile_pic
        }
        access_token = create_access_token(identity=identity)

        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['roles'] == []

    def test_get_user_info_deleted_user(self, test_app, client, user_role):
        """Should return empty roles when user no longer exists."""
        # Create a temporary user
        user = User(
            username='temp_user',
            email='temp@test.com',
            active=True,
            authenticate=True
        )
        user.set_password('testpassword123')
        user.roles.append(user_role)
        db.session.add(user)
        db.session.commit()

        user_id = user.id
        identity = {
            'id': user_id,
            'username': user.username,
            'email': user.email,
            'picture': user.profile_pic
        }
        access_token = create_access_token(identity=identity)

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        # Try to get user info with valid token but deleted user
        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        # User not found, should return empty roles
        assert data['roles'] == []

    def test_get_user_info_returns_identity_fields(self, test_app, client, user_role):
        """Should return all identity fields from JWT."""
        user = User(
            username='identity_test_user',
            email='identity_test@test.com',
            active=True,
            authenticate=True
        )
        user.set_password('testpassword123')
        user.roles.append(user_role)
        db.session.add(user)
        db.session.commit()

        identity = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'picture': 'https://example.com/pic.jpg'
        }
        access_token = create_access_token(identity=identity)

        response = client.get(
            '/api/auth/user_info',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == identity['id']
        assert data['username'] == identity['username']
        assert data['email'] == identity['email']
        assert data['picture'] == identity['picture']

        # Cleanup
        db.session.delete(user)
        db.session.commit()
