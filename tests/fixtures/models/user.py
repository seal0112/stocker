"""User and Role model fixtures for testing."""
import pytest
from app import db
from app.models.user import User
from app.models.role import Role


@pytest.fixture(scope='module')
def admin_role(test_app):
    """Create admin role for testing."""
    role = Role.query.filter_by(name='admin').first()
    if not role:
        role = Role(
            name='admin',
            description='Administrator',
            is_default=False
        )
        db.session.add(role)
        db.session.commit()

    yield role


@pytest.fixture(scope='module')
def moderator_role(test_app):
    """Create moderator role for testing."""
    role = Role.query.filter_by(name='moderator').first()
    if not role:
        role = Role(
            name='moderator',
            description='Moderator',
            is_default=False
        )
        db.session.add(role)
        db.session.commit()

    yield role


@pytest.fixture(scope='module')
def user_role(test_app):
    """Create default user role for testing."""
    role = Role.query.filter_by(name='user').first()
    if not role:
        role = Role(
            name='user',
            description='Regular User',
            is_default=True
        )
        db.session.add(role)
        db.session.commit()

    yield role


@pytest.fixture
def admin_user(test_app, admin_role):
    """Create an admin user for testing."""
    user = User(
        username='admin_test',
        email='admin@test.com',
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
def moderator_user(test_app, moderator_role):
    """Create a moderator user for testing."""
    user = User(
        username='moderator_test',
        email='moderator@test.com',
        active=True,
        authenticate=True
    )
    user.set_password('testpassword123')
    user.roles.append(moderator_role)
    db.session.add(user)
    db.session.commit()

    yield user

    # Cleanup
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def regular_user(test_app, user_role):
    """Create a regular user for testing."""
    user = User(
        username='regular_test',
        email='regular@test.com',
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
def user_no_roles(test_app):
    """Create a user with no roles for testing."""
    user = User(
        username='norole_test',
        email='norole@test.com',
        active=True,
        authenticate=True
    )
    user.set_password('testpassword123')
    db.session.add(user)
    db.session.commit()

    yield user

    # Cleanup
    db.session.delete(user)
    db.session.commit()
