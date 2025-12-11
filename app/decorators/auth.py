from functools import wraps

from flask import jsonify, request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app import db
from app.models import User, ApiToken


def role_required(*required_roles):
    """
    Decorator to check if the current user has any of the required roles.

    Usage:
        @role_required('admin')
        def admin_only_endpoint():
            ...

        @role_required('admin', 'moderator')
        def admin_or_moderator_endpoint():
            ...

    Args:
        *required_roles: One or more role names. User must have at least one.

    Returns:
        403 Forbidden if user doesn't have any of the required roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()

            user = db.session.query(User).filter_by(id=current_user['id']).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Check if user has any of the required roles
            user_roles = {role.name for role in user.roles}
            if not user_roles.intersection(set(required_roles)):
                return jsonify({
                    'error': 'Access denied',
                    'message': f'Required role(s): {", ".join(required_roles)}'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """
    Decorator to check if the current user has admin role.

    Usage:
        @admin_required
        def admin_only_endpoint():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_jwt_identity()

        user = db.session.query(User).filter_by(id=current_user['id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.has_role('admin'):
            return jsonify({
                'error': 'Access denied',
                'message': 'Admin role required'
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def moderator_required(fn):
    """
    Decorator to check if the current user has admin or moderator role.

    Usage:
        @moderator_required
        def moderator_endpoint():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_jwt_identity()

        user = db.session.query(User).filter_by(id=current_user['id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not (user.has_role('admin') or user.has_role('moderator')):
            return jsonify({
                'error': 'Access denied',
                'message': 'Admin or moderator role required'
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def permission_required(*required_permissions):
    """
    Decorator to check if the current user has any of the required permissions.

    Usage:
        @permission_required('feed:write')
        def create_feed():
            ...

        @permission_required('feed:write', 'feed:delete')
        def manage_feed():
            ...

    Args:
        *required_permissions: One or more permission names. User must have at least one.

    Returns:
        403 Forbidden if user doesn't have any of the required permissions.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()

            user = db.session.query(User).filter_by(id=current_user['id']).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Check if user has any of the required permissions
            has_permission = any(
                user.has_permission(perm) for perm in required_permissions
            )

            if not has_permission:
                return jsonify({
                    'error': 'Access denied',
                    'message': f'Required permission(s): {", ".join(required_permissions)}'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def api_auth_required(fn):
    """
    Decorator that supports both JWT and API token authentication.

    Checks Authorization header:
    - If token starts with 'stk_', validates as API token
    - Otherwise, falls back to JWT validation

    Sets g.current_user with user identity dict and g.auth_type with 'api_token' or 'jwt'.

    Usage:
        @api_auth_required
        def my_endpoint():
            user = g.current_user
            auth_type = g.auth_type
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        # Check if it's an API token
        if auth_header.startswith('Bearer stk_'):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            api_token = ApiToken.verify_token(token)

            if not api_token:
                return jsonify({'error': 'Invalid or expired API token'}), 401

            # Get user info
            user = db.session.query(User).filter_by(id=api_token.user_id).first()
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401

            # Check if user still has required role (admin or moderator)
            if not (user.has_role('admin') or user.has_role('moderator')):
                # Deactivate the token since user no longer has permission
                api_token.is_active = False
                db.session.commit()
                return jsonify({
                    'error': 'Access denied',
                    'message': 'API token revoked: user no longer has required role'
                }), 403

            # Set current user in g
            g.current_user = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'picture': user.profile_pic
            }
            g.auth_type = 'api_token'
            g.api_token = api_token

            return fn(*args, **kwargs)

        # Fall back to JWT authentication
        try:
            verify_jwt_in_request()
            g.current_user = get_jwt_identity()
            g.auth_type = 'jwt'
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({'error': 'Authentication required'}), 401

    return wrapper


def api_auth_or_jwt_required(fn):
    """
    Alias for api_auth_required for clarity.
    Supports both API token and JWT authentication.
    """
    return api_auth_required(fn)
