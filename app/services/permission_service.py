"""
Permission synchronization service.

This module handles syncing permissions from code constants to database.
"""
from app import db
from app.models.permission import Permission
from app.models.role import Role
from app.constants.permissions import Permissions, DEFAULT_ROLE_PERMISSIONS


def sync_permissions():
    """
    Sync permissions from constants to database.

    - Adds new permissions that exist in code but not in DB
    - Does NOT remove permissions that exist in DB but not in code
    - Updates role-permission mappings based on DEFAULT_ROLE_PERMISSIONS

    This function is idempotent and safe to run on every app startup.
    """
    # Sync all permissions
    for name, module, description in Permissions.ALL:
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(
                name=name,
                module=module,
                description=description
            )
            db.session.add(permission)

    db.session.commit()

    # Sync role-permission mappings
    sync_role_permissions()


def sync_role_permissions():
    """
    Sync default role-permission mappings.

    This ensures each role has at least the default permissions defined in code.
    It does NOT remove existing permissions from roles.
    """
    for role_name, permission_names in DEFAULT_ROLE_PERMISSIONS.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            continue

        # Admin gets all permissions handled specially in has_permission()
        if permission_names == ['*']:
            continue

        for perm_name in permission_names:
            permission = Permission.query.filter_by(name=perm_name).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)

    db.session.commit()
