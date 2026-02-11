"""Tests for permission_required and api_auth_required decorators."""
import pytest
from unittest.mock import patch, MagicMock
from flask import jsonify, g

from app import db
from app.models.user import User
from app.models.role import Role
from app.models.api_token import ApiToken
from app.decorators.auth import permission_required, api_auth_required, api_auth_or_jwt_required


class TestPermissionRequired:
    """Tests for permission_required decorator."""

    def test_admin_has_all_permissions(self, test_app, admin_user):
        """Admin user should pass any permission check."""
        @permission_required('read')
        def protected():
            return jsonify({'message': 'success'}), 200

        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_current_user',
                       return_value={'id': admin_user.id}):
                response, status = protected()
                assert status == 200

    def test_user_with_permission_can_access(self, test_app, regular_user, user_role, read_permission):
        """User whose role has the required permission should access."""
        user_role.add_permission(read_permission)
        db.session.commit()

        @permission_required('read')
        def protected():
            return jsonify({'message': 'success'}), 200

        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_current_user',
                       return_value={'id': regular_user.id}):
                response, status = protected()
                assert status == 200

        # Cleanup
        user_role.remove_permission(read_permission)
        db.session.commit()

    def test_user_without_permission_403(self, test_app, regular_user):
        """User without the required permission should get 403."""
        @permission_required('admin')
        def protected():
            return jsonify({'message': 'success'}), 200

        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_current_user',
                       return_value={'id': regular_user.id}):
                response, status = protected()
                assert status == 403
                assert response.get_json()['error'] == 'Access denied'

    def test_user_not_found_404(self, test_app):
        """Non-existent user should return 404."""
        @permission_required('read')
        def protected():
            return jsonify({'message': 'success'}), 200

        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_current_user',
                       return_value={'id': 99999}):
                response, status = protected()
                assert status == 404
                assert response.get_json()['error'] == 'User not found'

    def test_multiple_perms_any_match(self, test_app, regular_user, user_role, read_permission):
        """User with any one of multiple required permissions should access."""
        user_role.add_permission(read_permission)
        db.session.commit()

        @permission_required('read', 'write')
        def protected():
            return jsonify({'message': 'success'}), 200

        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_current_user',
                       return_value={'id': regular_user.id}):
                response, status = protected()
                assert status == 200

        # Cleanup
        user_role.remove_permission(read_permission)
        db.session.commit()

    def test_multiple_perms_none_match_403(self, test_app, regular_user):
        """User without any of the required permissions should get 403."""
        @permission_required('admin', 'superadmin')
        def protected():
            return jsonify({'message': 'success'}), 200

        with patch('app.decorators.auth.verify_jwt_in_request'):
            with patch('app.decorators.auth.get_current_user',
                       return_value={'id': regular_user.id}):
                response, status = protected()
                assert status == 403


class TestApiAuthRequired:
    """Tests for api_auth_required decorator."""

    def test_valid_api_token_admin_200(self, test_app, admin_user):
        """Valid API token for admin user should succeed."""
        token_obj, plain_token = ApiToken.create_token(
            user_id=admin_user.id, name='test-admin-token')

        @api_auth_required
        def protected():
            return jsonify({'message': 'success', 'auth_type': g.auth_type}), 200

        with test_app.test_request_context(
                headers={'Authorization': f'Bearer {plain_token}'}):
            response, status = protected()
            assert status == 200
            assert response.get_json()['auth_type'] == 'api_token'

        # Cleanup
        ApiToken.query.filter_by(id=token_obj.id).delete()
        db.session.commit()

    def test_valid_api_token_moderator_200(self, test_app, moderator_user):
        """Valid API token for moderator user should succeed."""
        token_obj, plain_token = ApiToken.create_token(
            user_id=moderator_user.id, name='test-mod-token')

        @api_auth_required
        def protected():
            return jsonify({'message': 'success'}), 200

        with test_app.test_request_context(
                headers={'Authorization': f'Bearer {plain_token}'}):
            response, status = protected()
            assert status == 200

        # Cleanup
        ApiToken.query.filter_by(id=token_obj.id).delete()
        db.session.commit()

    def test_regular_user_api_token_403(self, test_app, regular_user):
        """Regular user API token should get 403 (role check fails, token deactivated)."""
        token_obj, plain_token = ApiToken.create_token(
            user_id=regular_user.id, name='test-regular-token')

        @api_auth_required
        def protected():
            return jsonify({'message': 'success'}), 200

        with test_app.test_request_context(
                headers={'Authorization': f'Bearer {plain_token}'}):
            response, status = protected()
            assert status == 403
            assert 'revoked' in response.get_json()['message']

        # Cleanup
        ApiToken.query.filter_by(id=token_obj.id).delete()
        db.session.commit()

    def test_invalid_api_token_401(self, test_app):
        """Invalid API token should return 401."""
        @api_auth_required
        def protected():
            return jsonify({'message': 'success'}), 200

        with test_app.test_request_context(
                headers={'Authorization': 'Bearer stk_invalidtoken12345678'}):
            response, status = protected()
            assert status == 401
            assert response.get_json()['error'] == 'Invalid or expired API token'

    def test_inactive_user_401(self, test_app, user_role):
        """API token for inactive user should return 401."""
        user = User(username='inactive_api_test', email='inactive_api@test.com',
                     active=False, authenticate=True)
        user.set_password('testpassword123')
        user.roles.append(user_role)
        db.session.add(user)
        db.session.commit()

        token_obj, plain_token = ApiToken.create_token(
            user_id=user.id, name='test-inactive-token')

        @api_auth_required
        def protected():
            return jsonify({'message': 'success'}), 200

        with test_app.test_request_context(
                headers={'Authorization': f'Bearer {plain_token}'}):
            response, status = protected()
            assert status == 401
            assert 'inactive' in response.get_json()['error'].lower() or \
                   'not found' in response.get_json()['error'].lower()

        # Cleanup
        ApiToken.query.filter_by(id=token_obj.id).delete()
        db.session.delete(user)
        db.session.commit()

    def test_jwt_fallback_success(self, test_app, regular_user):
        """Non-stk_ Bearer token should fall back to JWT validation."""
        @api_auth_required
        def protected():
            return jsonify({'message': 'success', 'auth_type': g.auth_type}), 200

        with test_app.test_request_context(
                headers={'Authorization': 'Bearer some-jwt-token'}):
            with patch('app.decorators.auth.verify_jwt_in_request'):
                with patch('app.decorators.auth.get_current_user',
                           return_value={'id': regular_user.id}):
                    response, status = protected()
                    assert status == 200
                    assert response.get_json()['auth_type'] == 'jwt'

    def test_invalid_jwt_401(self, test_app):
        """Invalid JWT should return 401."""
        @api_auth_required
        def protected():
            return jsonify({'message': 'success'}), 200

        with test_app.test_request_context(
                headers={'Authorization': 'Bearer invalid-jwt-token'}):
            with patch('app.decorators.auth.verify_jwt_in_request',
                       side_effect=Exception('Invalid JWT')):
                response, status = protected()
                assert status == 401
                assert response.get_json()['error'] == 'Authentication required'

    def test_no_auth_header_401(self, test_app):
        """Request with no Authorization header should return 401."""
        @api_auth_required
        def protected():
            return jsonify({'message': 'success'}), 200

        with test_app.test_request_context():
            with patch('app.decorators.auth.verify_jwt_in_request',
                       side_effect=Exception('Missing auth')):
                response, status = protected()
                assert status == 401

    def test_sets_g_current_user_and_auth_type(self, test_app, admin_user):
        """api_auth_required should set g.current_user and g.auth_type."""
        token_obj, plain_token = ApiToken.create_token(
            user_id=admin_user.id, name='test-g-token')

        @api_auth_required
        def protected():
            return jsonify({
                'user_id': g.current_user['id'],
                'username': g.current_user['username'],
                'auth_type': g.auth_type
            }), 200

        with test_app.test_request_context(
                headers={'Authorization': f'Bearer {plain_token}'}):
            response, status = protected()
            assert status == 200
            data = response.get_json()
            assert data['user_id'] == admin_user.id
            assert data['username'] == admin_user.username
            assert data['auth_type'] == 'api_token'

        # Cleanup
        ApiToken.query.filter_by(id=token_obj.id).delete()
        db.session.commit()

    def test_api_auth_or_jwt_required_is_alias(self):
        """api_auth_or_jwt_required should produce the same decorated result as api_auth_required."""
        def sample(): pass
        result1 = api_auth_required(sample)
        result2 = api_auth_or_jwt_required(sample)
        # Both should wrap the function with the same wrapper logic
        assert result1.__wrapped__ is sample
        assert result2.__wrapped__ is sample
