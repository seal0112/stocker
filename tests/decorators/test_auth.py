"""Unit tests for auth decorators."""
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token

from app.decorators.auth import role_required, admin_required, moderator_required


class TestRoleRequired:
    """Tests for role_required decorator."""

    def test_user_with_required_role_can_access(self, test_app, admin_user):
        """User with the required role should be able to access the endpoint."""
        with test_app.app_context():
            # Create a test endpoint with the decorator
            @role_required('admin')
            def protected_endpoint():
                return jsonify({'message': 'success'}), 200

            # Mock JWT verification and identity
            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': admin_user.id}):
                    response, status_code = protected_endpoint()
                    assert status_code == 200
                    assert response.get_json()['message'] == 'success'

    def test_user_without_required_role_gets_403(self, test_app, regular_user):
        """User without the required role should get 403 Forbidden."""
        with test_app.app_context():
            @role_required('admin')
            def protected_endpoint():
                return jsonify({'message': 'success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': regular_user.id}):
                    response, status_code = protected_endpoint()
                    assert status_code == 403
                    assert response.get_json()['error'] == 'Access denied'

    def test_user_not_found_returns_404(self, test_app):
        """Non-existent user should return 404."""
        with test_app.app_context():
            @role_required('admin')
            def protected_endpoint():
                return jsonify({'message': 'success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': 99999}):
                    response, status_code = protected_endpoint()
                    assert status_code == 404
                    assert response.get_json()['error'] == 'User not found'

    def test_multiple_roles_or_logic(self, test_app, moderator_user):
        """User with any one of multiple required roles should be able to access."""
        with test_app.app_context():
            @role_required('admin', 'moderator')
            def protected_endpoint():
                return jsonify({'message': 'success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': moderator_user.id}):
                    response, status_code = protected_endpoint()
                    assert status_code == 200
                    assert response.get_json()['message'] == 'success'

    def test_multiple_roles_none_match_gets_403(self, test_app, regular_user):
        """User without any of the required roles should get 403."""
        with test_app.app_context():
            @role_required('admin', 'moderator')
            def protected_endpoint():
                return jsonify({'message': 'success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': regular_user.id}):
                    response, status_code = protected_endpoint()
                    assert status_code == 403


class TestAdminRequired:
    """Tests for admin_required decorator."""

    def test_admin_can_access(self, test_app, admin_user):
        """Admin user should be able to access admin-only endpoint."""
        with test_app.app_context():
            @admin_required
            def admin_endpoint():
                return jsonify({'message': 'admin success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': admin_user.id}):
                    response, status_code = admin_endpoint()
                    assert status_code == 200
                    assert response.get_json()['message'] == 'admin success'

    def test_non_admin_gets_403(self, test_app, regular_user):
        """Non-admin user should get 403 Forbidden."""
        with test_app.app_context():
            @admin_required
            def admin_endpoint():
                return jsonify({'message': 'admin success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': regular_user.id}):
                    response, status_code = admin_endpoint()
                    assert status_code == 403
                    assert response.get_json()['error'] == 'Access denied'
                    assert 'Admin role required' in response.get_json()['message']

    def test_moderator_cannot_access_admin_endpoint(self, test_app, moderator_user):
        """Moderator should not be able to access admin-only endpoint."""
        with test_app.app_context():
            @admin_required
            def admin_endpoint():
                return jsonify({'message': 'admin success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': moderator_user.id}):
                    response, status_code = admin_endpoint()
                    assert status_code == 403

    def test_user_not_found_returns_404(self, test_app):
        """Non-existent user should return 404."""
        with test_app.app_context():
            @admin_required
            def admin_endpoint():
                return jsonify({'message': 'admin success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': 99999}):
                    response, status_code = admin_endpoint()
                    assert status_code == 404
                    assert response.get_json()['error'] == 'User not found'


class TestModeratorRequired:
    """Tests for moderator_required decorator."""

    def test_admin_can_access_moderator_endpoint(self, test_app, admin_user):
        """Admin should be able to access moderator endpoint (admin inherits access)."""
        with test_app.app_context():
            @moderator_required
            def moderator_endpoint():
                return jsonify({'message': 'moderator success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': admin_user.id}):
                    response, status_code = moderator_endpoint()
                    assert status_code == 200
                    assert response.get_json()['message'] == 'moderator success'

    def test_moderator_can_access(self, test_app, moderator_user):
        """Moderator user should be able to access moderator endpoint."""
        with test_app.app_context():
            @moderator_required
            def moderator_endpoint():
                return jsonify({'message': 'moderator success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': moderator_user.id}):
                    response, status_code = moderator_endpoint()
                    assert status_code == 200
                    assert response.get_json()['message'] == 'moderator success'

    def test_regular_user_gets_403(self, test_app, regular_user):
        """Regular user should get 403 Forbidden."""
        with test_app.app_context():
            @moderator_required
            def moderator_endpoint():
                return jsonify({'message': 'moderator success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': regular_user.id}):
                    response, status_code = moderator_endpoint()
                    assert status_code == 403
                    assert response.get_json()['error'] == 'Access denied'
                    assert 'Admin or moderator role required' in response.get_json()['message']

    def test_user_not_found_returns_404(self, test_app):
        """Non-existent user should return 404."""
        with test_app.app_context():
            @moderator_required
            def moderator_endpoint():
                return jsonify({'message': 'moderator success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': 99999}):
                    response, status_code = moderator_endpoint()
                    assert status_code == 404
                    assert response.get_json()['error'] == 'User not found'

    def test_user_with_no_roles_gets_403(self, test_app, user_no_roles):
        """User with no roles should get 403 Forbidden."""
        with test_app.app_context():
            @moderator_required
            def moderator_endpoint():
                return jsonify({'message': 'moderator success'}), 200

            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_jwt_identity', return_value={'id': user_no_roles.id}):
                    response, status_code = moderator_endpoint()
                    assert status_code == 403


class TestUserRoleAssignment:
    """Tests for user role assignment functionality."""

    def test_user_can_have_multiple_roles(self, test_app, admin_role, moderator_role, user_role):
        """User can be assigned multiple roles."""
        with test_app.app_context():
            from app import db
            from app.models.user import User

            user = User(
                username='multi_role_test',
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

            assert len(user.roles) == 3
            assert user.has_role('user')
            assert user.has_role('admin')
            assert user.has_role('moderator')

            # Cleanup
            db.session.delete(user)
            db.session.commit()

    def test_user_gets_default_user_role_on_creation(self, test_app, user_role):
        """User should get user role by default when using assign_default_role."""
        with test_app.app_context():
            from app import db
            from app.models.user import User

            user = User(
                username='default_role_test',
                email='default_role@test.com',
                active=True,
                authenticate=True
            )
            user.set_password('testpassword123')
            db.session.add(user)
            db.session.commit()

            # User initially has no roles
            assert len(user.roles) == 0

            # Assign default role
            user.assign_default_role()
            db.session.commit()

            assert len(user.roles) == 1
            assert user.has_role('user')

            # Cleanup
            db.session.delete(user)
            db.session.commit()

    def test_admin_can_add_role_to_user(self, test_app, regular_user, moderator_role):
        """Admin can assign roles to users."""
        with test_app.app_context():
            from app import db

            # Verify user starts with only user role
            assert len(regular_user.roles) == 1
            assert regular_user.has_role('user')

            # Add moderator role
            regular_user.add_role(moderator_role)
            db.session.commit()

            assert len(regular_user.roles) == 2
            assert regular_user.has_role('user')
            assert regular_user.has_role('moderator')

    def test_admin_can_remove_non_user_role(self, test_app, user_role, moderator_role):
        """Admin can remove non-user roles from users."""
        with test_app.app_context():
            from app import db
            from app.models.user import User

            user = User(
                username='remove_role_test',
                email='remove_role@test.com',
                active=True,
                authenticate=True
            )
            user.set_password('testpassword123')
            user.roles.append(user_role)
            user.roles.append(moderator_role)
            db.session.add(user)
            db.session.commit()

            assert len(user.roles) == 2
            assert user.has_role('moderator')

            # Remove moderator role
            user.remove_role(moderator_role)
            db.session.commit()

            assert len(user.roles) == 1
            assert not user.has_role('moderator')
            assert user.has_role('user')

            # Cleanup
            db.session.delete(user)
            db.session.commit()

    def test_user_role_cannot_be_removed(self, test_app, regular_user, user_role):
        """User role cannot be removed from user."""
        with test_app.app_context():
            assert regular_user.has_role('user')

            # Try to remove user role - should raise ValueError
            with pytest.raises(ValueError, match="Cannot remove user role"):
                regular_user.remove_role(user_role)

            # Verify user role is still present
            assert regular_user.has_role('user')

    def test_adding_same_role_twice_does_not_duplicate(self, test_app, regular_user, moderator_role):
        """Adding the same role twice should not create duplicates."""
        with test_app.app_context():
            from app import db

            initial_role_count = len(regular_user.roles)

            regular_user.add_role(moderator_role)
            db.session.commit()
            assert len(regular_user.roles) == initial_role_count + 1

            # Add the same role again
            regular_user.add_role(moderator_role)
            db.session.commit()
            assert len(regular_user.roles) == initial_role_count + 1  # Should not increase

    def test_role_names_property(self, test_app, user_role, admin_role):
        """Test role_names property returns list of role names."""
        with test_app.app_context():
            from app import db
            from app.models.user import User

            user = User(
                username='role_names_test',
                email='role_names@test.com',
                active=True,
                authenticate=True
            )
            user.set_password('testpassword123')
            user.roles.append(user_role)
            user.roles.append(admin_role)
            db.session.add(user)
            db.session.commit()

            role_names = user.role_names
            assert 'user' in role_names
            assert 'admin' in role_names
            assert len(role_names) == 2

            # Cleanup
            db.session.delete(user)
            db.session.commit()
