import logging

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.decorators import admin_required
from . import user_management, roles_bp
from .user_service import UserService
from .serializer import (
    user_schema,
    users_schema,
    roles_schema,
    update_user_roles_schema,
    update_user_status_schema
)

logger = logging.getLogger(__name__)
user_service = UserService()


class UserListView(MethodView):
    """API for listing all users."""

    @admin_required
    def get(self):
        """List all users."""
        users = user_service.get_all_users()

        # Transform users to include role names
        result = []
        for user in users:
            user_data = user_schema.dump(user)
            user_data['roles'] = user.role_names
            result.append(user_data)

        return jsonify({
            "data": result,
            "total": len(result)
        }), 200


class UserDetailView(MethodView):
    """API for getting a specific user."""

    @admin_required
    def get(self, user_id):
        """Get a specific user by ID."""
        user = user_service.get_user_by_id(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = user_schema.dump(user)
        user_data['roles'] = user.role_names
        return jsonify(user_data), 200


class UserRolesView(MethodView):
    """API for updating user roles."""

    @admin_required
    def patch(self, user_id):
        """Update user roles."""
        current_user = get_jwt_identity()

        # Validate request body
        try:
            data = update_user_roles_schema.load(request.get_json() or {})
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400

        # Update roles
        try:
            user = user_service.update_user_roles(
                user_id=user_id,
                role_names=data['role_names'],
                assigned_by=current_user['id']
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user roles: {e}", exc_info=True)
            return jsonify({"error": "Failed to update user roles"}), 500

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = user_schema.dump(user)
        user_data['roles'] = user.role_names
        return jsonify(user_data), 200


class UserStatusView(MethodView):
    """API for updating user active status."""

    @admin_required
    def patch(self, user_id):
        """Update user active status."""
        # Validate request body
        try:
            data = update_user_status_schema.load(request.get_json() or {})
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400

        # Update status
        try:
            user = user_service.update_user_status(
                user_id=user_id,
                active=data['active']
            )
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user status: {e}", exc_info=True)
            return jsonify({"error": "Failed to update user status"}), 500

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = user_schema.dump(user)
        user_data['roles'] = user.role_names
        return jsonify(user_data), 200


class RoleListView(MethodView):
    """API for listing all roles."""

    @admin_required
    def get(self):
        """List all available roles."""
        roles = user_service.get_all_roles()
        return jsonify({
            "data": roles_schema.dump(roles)
        }), 200


# Register URL rules for user_management blueprint
user_management.add_url_rule(
    '',
    view_func=UserListView.as_view('user_list'),
    methods=['GET']
)

user_management.add_url_rule(
    '/<int:user_id>',
    view_func=UserDetailView.as_view('user_detail'),
    methods=['GET']
)

user_management.add_url_rule(
    '/<int:user_id>/roles',
    view_func=UserRolesView.as_view('user_roles'),
    methods=['PATCH']
)

user_management.add_url_rule(
    '/<int:user_id>/status',
    view_func=UserStatusView.as_view('user_status'),
    methods=['PATCH']
)

# Register URL rules for roles blueprint
roles_bp.add_url_rule(
    '',
    view_func=RoleListView.as_view('role_list'),
    methods=['GET']
)
