"""Permission model fixtures for testing."""
import pytest
from app import db
from app.models.permission import Permission, role_permission


@pytest.fixture(scope='module')
def read_permission(test_app):
    """Create a read permission for testing."""
    permission = Permission.query.filter_by(name='read').first()
    if not permission:
        permission = Permission(
            name='read',
            module='general',
            description='Read access'
        )
        db.session.add(permission)
        db.session.commit()

    yield permission


@pytest.fixture(scope='module')
def write_permission(test_app):
    """Create a write permission for testing."""
    permission = Permission.query.filter_by(name='write').first()
    if not permission:
        permission = Permission(
            name='write',
            module='general',
            description='Write access'
        )
        db.session.add(permission)
        db.session.commit()

    yield permission


@pytest.fixture(scope='module')
def delete_permission(test_app):
    """Create a delete permission for testing."""
    permission = Permission.query.filter_by(name='delete').first()
    if not permission:
        permission = Permission(
            name='delete',
            module='general',
            description='Delete access'
        )
        db.session.add(permission)
        db.session.commit()

    yield permission


@pytest.fixture(scope='module')
def admin_permission(test_app):
    """Create an admin permission for testing."""
    permission = Permission.query.filter_by(name='admin').first()
    if not permission:
        permission = Permission(
            name='admin',
            module='admin',
            description='Full admin access'
        )
        db.session.add(permission)
        db.session.commit()

    yield permission


@pytest.fixture(scope='module')
def stock_read_permission(test_app):
    """Create a stock read permission for testing."""
    permission = Permission.query.filter_by(name='stock:read').first()
    if not permission:
        permission = Permission(
            name='stock:read',
            module='stock',
            description='Read stock data'
        )
        db.session.add(permission)
        db.session.commit()

    yield permission


@pytest.fixture(scope='module')
def stock_write_permission(test_app):
    """Create a stock write permission for testing."""
    permission = Permission.query.filter_by(name='stock:write').first()
    if not permission:
        permission = Permission(
            name='stock:write',
            module='stock',
            description='Write stock data'
        )
        db.session.add(permission)
        db.session.commit()

    yield permission


@pytest.fixture(scope='module')
def role_with_permissions(test_app, admin_role, read_permission, write_permission):
    """Create an admin role with read and write permissions."""
    # Add permissions to role if not already added
    stmt = role_permission.select().where(
        role_permission.c.role_id == admin_role.id,
        role_permission.c.permission_id == read_permission.id
    )
    if not db.session.execute(stmt).first():
        db.session.execute(
            role_permission.insert().values(
                role_id=admin_role.id,
                permission_id=read_permission.id
            )
        )

    stmt = role_permission.select().where(
        role_permission.c.role_id == admin_role.id,
        role_permission.c.permission_id == write_permission.id
    )
    if not db.session.execute(stmt).first():
        db.session.execute(
            role_permission.insert().values(
                role_id=admin_role.id,
                permission_id=write_permission.id
            )
        )

    db.session.commit()

    yield admin_role
