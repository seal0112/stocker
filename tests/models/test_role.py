"""Tests for Role model."""
import pytest

from app import db
from app.models.role import Role
from app.models.permission import Permission


class TestRoleModel:
    """Tests for Role model methods."""

    def test_get_default_role_returns_default(self, test_app, user_role):
        """get_default_role should return the role with is_default=True."""
        default = Role.get_default_role()
        assert default is not None
        assert default.name == 'user'
        assert default.is_default is True

    def test_set_default_role_changes_default(self, test_app, user_role, admin_role):
        """set_default_role should change which role is default."""
        result = Role.set_default_role('admin')
        assert result is not None
        assert result.name == 'admin'
        assert result.is_default is True

        # Previous default should no longer be default
        refreshed_user_role = Role.query.filter_by(name='user').first()
        assert refreshed_user_role.is_default is False

        # Restore original default
        Role.set_default_role('user')

    def test_set_default_role_nonexistent_returns_none(self, test_app):
        """set_default_role with nonexistent role name should return None."""
        result = Role.set_default_role('nonexistent_role_xyz')
        assert result is None

    def test_admin_has_permission_always_true(self, test_app, admin_role):
        """Admin role should have all permissions (returns True for any name)."""
        assert admin_role.has_permission('read') is True
        assert admin_role.has_permission('write') is True
        assert admin_role.has_permission('anything') is True

    def test_role_with_permission_returns_true(self, test_app, user_role, read_permission):
        """Role with a specific permission should return True for has_permission."""
        user_role.add_permission(read_permission)
        db.session.commit()

        assert user_role.has_permission('read') is True

        # Cleanup
        user_role.remove_permission(read_permission)
        db.session.commit()

    def test_role_without_permission_returns_false(self, test_app, user_role):
        """Role without a specific permission should return False."""
        assert user_role.has_permission('delete') is False

    def test_add_permission(self, test_app, moderator_role, write_permission):
        """add_permission should add a permission to the role."""
        moderator_role.add_permission(write_permission)
        db.session.commit()

        assert write_permission in moderator_role.permissions

        # Cleanup
        moderator_role.remove_permission(write_permission)
        db.session.commit()

    def test_add_duplicate_permission_no_op(self, test_app, moderator_role, read_permission):
        """Adding the same permission twice should not duplicate it."""
        moderator_role.add_permission(read_permission)
        db.session.commit()
        count_before = len(moderator_role.permissions)

        moderator_role.add_permission(read_permission)
        db.session.commit()
        count_after = len(moderator_role.permissions)

        assert count_before == count_after

        # Cleanup
        moderator_role.remove_permission(read_permission)
        db.session.commit()

    def test_remove_permission(self, test_app, moderator_role, read_permission):
        """remove_permission should remove a permission from the role."""
        moderator_role.add_permission(read_permission)
        db.session.commit()
        assert read_permission in moderator_role.permissions

        moderator_role.remove_permission(read_permission)
        db.session.commit()
        assert read_permission not in moderator_role.permissions

    def test_remove_nonexistent_permission_no_op(self, test_app, moderator_role, delete_permission):
        """Removing a permission the role doesn't have should be a no-op."""
        initial_count = len(moderator_role.permissions)
        moderator_role.remove_permission(delete_permission)
        db.session.commit()
        assert len(moderator_role.permissions) == initial_count

    def test_permission_names_admin_returns_wildcard(self, test_app, admin_role):
        """Admin role permission_names should return ['*']."""
        assert admin_role.permission_names == ['*']

    def test_permission_names_normal_role(self, test_app, moderator_role, read_permission, write_permission):
        """Normal role permission_names should return list of permission names."""
        moderator_role.add_permission(read_permission)
        moderator_role.add_permission(write_permission)
        db.session.commit()

        names = moderator_role.permission_names
        assert 'read' in names
        assert 'write' in names

        # Cleanup
        moderator_role.remove_permission(read_permission)
        moderator_role.remove_permission(write_permission)
        db.session.commit()
