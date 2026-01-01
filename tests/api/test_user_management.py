"""API tests for user management endpoints."""
import pytest
import json
from unittest.mock import patch

from app import db
from app.models.user import User
from app.models.role import Role


@pytest.fixture
def admin_user_for_api(test_app):
    """Create an admin user for API tests."""
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator', is_default=False)
        db.session.add(admin_role)
        db.session.commit()

    user = User(
        username='admin_api_test',
        email='admin_api@test.com',
        active=True,
        authenticate=True
    )
    user.set_password('testpassword123')
    user.roles.append(admin_role)
    db.session.add(user)
    db.session.commit()

    yield user

    # Cleanup
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def regular_user_for_api(test_app):
    """Create a regular user for API tests."""
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular User', is_default=True)
        db.session.add(user_role)
        db.session.commit()

    user = User(
        username='regular_api_test',
        email='regular_api@test.com',
        active=True,
        authenticate=True
    )
    user.set_password('testpassword123')
    user.roles.append(user_role)
    db.session.add(user)
    db.session.commit()

    yield user

    # Cleanup
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def target_user(test_app):
    """Create a target user to be managed."""
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular User', is_default=True)
        db.session.add(user_role)
        db.session.commit()

    user = User(
        username='target_user',
        email='target@test.com',
        active=True,
        authenticate=True
    )
    user.set_password('testpassword123')
    user.roles.append(user_role)
    db.session.add(user)
    db.session.commit()

    yield user

    # Cleanup
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def admin_auth_headers(admin_user_for_api):
    """Create mock JWT auth headers for admin user."""
    return {
        'user_identity': {
            'id': admin_user_for_api.id,
            'username': admin_user_for_api.username,
            'email': admin_user_for_api.email,
            'picture': None
        }
    }


@pytest.fixture
def regular_auth_headers(regular_user_for_api):
    """Create mock JWT auth headers for regular user."""
    return {
        'user_identity': {
            'id': regular_user_for_api.id,
            'username': regular_user_for_api.username,
            'email': regular_user_for_api.email,
            'picture': None
        }
    }


@pytest.fixture
def all_roles(test_app):
    """Ensure all roles exist for testing."""
    roles = {}
    for role_name, desc, is_default in [
        ('admin', 'Administrator', False),
        ('moderator', 'Moderator', False),
        ('user', 'Regular User', True)
    ]:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=desc, is_default=is_default)
            db.session.add(role)
            db.session.commit()
        roles[role_name] = role
    return roles


class TestUserListEndpoint:
    """Tests for GET /api/v1/users."""

    def test_list_users_as_admin(self, client, admin_user_for_api, admin_auth_headers):
        """Admin should be able to list all users."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                response = client.get('/api/v1/users')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'data' in data
                assert 'total' in data
                assert isinstance(data['data'], list)

    def test_list_users_as_regular_user_forbidden(self, client, regular_user_for_api, regular_auth_headers):
        """Regular user should get 403 when trying to list users."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=regular_auth_headers['user_identity']):
                response = client.get('/api/v1/users')
                assert response.status_code == 403
                data = json.loads(response.data)
                assert 'error' in data

    def test_list_users_includes_roles(self, client, admin_user_for_api, admin_auth_headers, target_user):
        """Listed users should include their roles."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                response = client.get('/api/v1/users')
                assert response.status_code == 200
                data = json.loads(response.data)

                # Find target user in the list
                target_in_list = next(
                    (u for u in data['data'] if u['username'] == 'target_user'),
                    None
                )
                assert target_in_list is not None
                assert 'roles' in target_in_list
                assert 'user' in target_in_list['roles']


class TestUserDetailEndpoint:
    """Tests for GET /api/v1/users/<user_id>."""

    def test_get_user_as_admin(self, client, admin_user_for_api, admin_auth_headers, target_user):
        """Admin should be able to get user details."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                response = client.get(f'/api/v1/users/{target_user.id}')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['username'] == 'target_user'
                assert data['email'] == 'target@test.com'
                assert 'roles' in data

    def test_get_user_as_regular_user_forbidden(self, client, regular_user_for_api, regular_auth_headers, target_user):
        """Regular user should get 403 when trying to get user details."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=regular_auth_headers['user_identity']):
                response = client.get(f'/api/v1/users/{target_user.id}')
                assert response.status_code == 403

    def test_get_user_not_found(self, client, admin_user_for_api, admin_auth_headers):
        """Should return 404 for non-existent user."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                response = client.get('/api/v1/users/99999')
                assert response.status_code == 404
                data = json.loads(response.data)
                assert 'error' in data


class TestUserRolesEndpoint:
    """Tests for PATCH /api/v1/users/<user_id>/roles."""

    def test_update_roles_as_admin(self, client, admin_user_for_api, admin_auth_headers, target_user, all_roles):
        """Admin should be able to update user roles."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                with patch('app.user_management.views.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                    response = client.patch(
                        f'/api/v1/users/{target_user.id}/roles',
                        data=json.dumps({'role_names': ['moderator', 'user']}),
                        content_type='application/json'
                    )
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert 'moderator' in data['roles']
                    assert 'user' in data['roles']

    def test_update_roles_as_regular_user_forbidden(self, client, regular_user_for_api, regular_auth_headers, target_user):
        """Regular user should get 403 when trying to update roles."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=regular_auth_headers['user_identity']):
                response = client.patch(
                    f'/api/v1/users/{target_user.id}/roles',
                    data=json.dumps({'role_names': ['admin']}),
                    content_type='application/json'
                )
                assert response.status_code == 403

    def test_update_roles_user_not_found(self, client, admin_user_for_api, admin_auth_headers, all_roles):
        """Should return 404 for non-existent user."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                with patch('app.user_management.views.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                    response = client.patch(
                        '/api/v1/users/99999/roles',
                        data=json.dumps({'role_names': ['user']}),
                        content_type='application/json'
                    )
                    assert response.status_code == 404

    def test_update_roles_invalid_role(self, client, admin_user_for_api, admin_auth_headers, target_user):
        """Should return 400 for invalid role name."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                with patch('app.user_management.views.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                    response = client.patch(
                        f'/api/v1/users/{target_user.id}/roles',
                        data=json.dumps({'role_names': ['invalid_role']}),
                        content_type='application/json'
                    )
                    assert response.status_code == 400
                    data = json.loads(response.data)
                    assert 'error' in data

    def test_update_roles_missing_body(self, client, admin_user_for_api, admin_auth_headers, target_user):
        """Should return 400 when request body is missing."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                with patch('app.user_management.views.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                    response = client.patch(
                        f'/api/v1/users/{target_user.id}/roles',
                        data=json.dumps({}),
                        content_type='application/json'
                    )
                    assert response.status_code == 400

    def test_update_roles_adds_user_role_automatically(self, client, admin_user_for_api, admin_auth_headers, target_user, all_roles):
        """User role should be added automatically even if not specified."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                with patch('app.user_management.views.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                    response = client.patch(
                        f'/api/v1/users/{target_user.id}/roles',
                        data=json.dumps({'role_names': ['admin']}),
                        content_type='application/json'
                    )
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert 'admin' in data['roles']
                    assert 'user' in data['roles']  # user role should be added automatically


class TestRoleListEndpoint:
    """Tests for GET /api/v1/roles."""

    def test_list_roles_as_admin(self, client, admin_user_for_api, admin_auth_headers, all_roles):
        """Admin should be able to list all roles."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                response = client.get('/api/v1/roles')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'data' in data
                assert isinstance(data['data'], list)

                role_names = [r['name'] for r in data['data']]
                assert 'admin' in role_names
                assert 'moderator' in role_names
                assert 'user' in role_names

    def test_list_roles_as_regular_user_forbidden(self, client, regular_user_for_api, regular_auth_headers):
        """Regular user should get 403 when trying to list roles."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=regular_auth_headers['user_identity']):
                response = client.get('/api/v1/roles')
                assert response.status_code == 403

    def test_list_roles_includes_description(self, client, admin_user_for_api, admin_auth_headers, all_roles):
        """Listed roles should include description."""
        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_jwt_identity', return_value=admin_auth_headers['user_identity']):
                response = client.get('/api/v1/roles')
                assert response.status_code == 200
                data = json.loads(response.data)

                for role in data['data']:
                    assert 'id' in role
                    assert 'name' in role
                    assert 'description' in role
