"""User and Role model fixtures for testing."""
import pytest
from app import db
from app.models.user import User
from app.models.role import Role
from app.models.api_token import ApiToken


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

    # Cleanup - delete FK-referencing tables first (children -> parent)
    ApiToken.query.filter_by(user_id=user.id).delete()
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

    # Cleanup - delete associated tokens first to avoid FK constraint
    ApiToken.query.filter_by(user_id=user.id).delete()
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

    # Cleanup - delete associated tokens first to avoid FK constraint
    ApiToken.query.filter_by(user_id=user.id).delete()
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

    # Cleanup - delete associated tokens first to avoid FK constraint
    ApiToken.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def multi_role_user(test_app, user_role, admin_role, moderator_role):
    """Create a user with multiple roles for testing."""
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

    yield user

    # Cleanup - delete associated tokens first to avoid FK constraint
    ApiToken.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def deleted_user_token(test_app, user_role):
    """Create a token for a user that will be deleted."""
    """建立一個使用者，產生 Token 後將其刪除，並回傳該 Token"""
    from flask_jwt_extended import create_access_token

    user = User(username='ghost', email='ghost@test.com')
    user.roles.append(user_role)
    db.session.add(user)
    db.session.commit()

    # 2. 產生身份與 Token
    identity = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'picture': user.profile_pic
    }
    token = create_access_token(identity=identity)

    # 3. 刪除使用者
    db.session.delete(user)
    db.session.commit()

    return token
