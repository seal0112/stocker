"""ApiToken model fixtures for testing."""
import pytest
from datetime import datetime, timedelta
from app import db
from app.models.api_token import ApiToken


@pytest.fixture
def sample_api_token(test_app, regular_user):
    """Create a sample API token for testing."""
    api_token, plain_token = ApiToken.create_token(
        user_id=regular_user.id,
        name='Test Token',
        scopes=['read', 'write']
    )

    yield api_token, plain_token

    # Cleanup
    db.session.delete(api_token)
    db.session.commit()


@pytest.fixture
def sample_api_token_readonly(test_app, regular_user):
    """Create a read-only API token for testing."""
    api_token, plain_token = ApiToken.create_token(
        user_id=regular_user.id,
        name='Read Only Token',
        scopes=['read']
    )

    yield api_token, plain_token

    # Cleanup
    db.session.delete(api_token)
    db.session.commit()


@pytest.fixture
def expired_api_token(test_app, regular_user):
    """Create an expired API token for testing."""
    api_token, plain_token = ApiToken.create_token(
        user_id=regular_user.id,
        name='Expired Token',
        scopes=['read'],
        expires_at=datetime.utcnow() - timedelta(days=1)
    )

    yield api_token, plain_token

    # Cleanup
    db.session.delete(api_token)
    db.session.commit()


@pytest.fixture
def admin_api_token(test_app, admin_user):
    """Create an admin API token for testing."""
    api_token, plain_token = ApiToken.create_token(
        user_id=admin_user.id,
        name='Admin Token',
        scopes=['read', 'write', 'admin']
    )

    yield api_token, plain_token

    # Cleanup
    db.session.delete(api_token)
    db.session.commit()
