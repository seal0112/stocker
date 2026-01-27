"""Authentication fixtures for API tests."""
import pytest
from flask_jwt_extended import create_access_token


@pytest.fixture
def auth_headers(test_app, regular_user):
    """Create JWT auth headers for authenticated requests.

    Flask-JWT-Extended 4.x requires identity to be a string.
    Additional user info is passed via additional_claims.
    """
    additional_claims = {
        'username': regular_user.username,
        'email': regular_user.email,
        'picture': regular_user.profile_pic
    }
    access_token = create_access_token(
        identity=str(regular_user.id),
        additional_claims=additional_claims
    )
    return {'Authorization': f'Bearer {access_token}'}


class AuthenticatedClient:
    """Test client wrapper that includes auth headers in all requests."""

    def __init__(self, client, headers):
        self._client = client
        self._headers = headers

    def get(self, *args, **kwargs):
        kwargs.setdefault('headers', {}).update(self._headers)
        return self._client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs.setdefault('headers', {}).update(self._headers)
        return self._client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs.setdefault('headers', {}).update(self._headers)
        return self._client.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs.setdefault('headers', {}).update(self._headers)
        return self._client.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('headers', {}).update(self._headers)
        return self._client.delete(*args, **kwargs)


@pytest.fixture
def authenticated_client(test_app, auth_headers):
    """Create a test client wrapper with regular user auth."""
    client = test_app.test_client()
    return AuthenticatedClient(client, auth_headers)


@pytest.fixture
def moderator_auth_headers(test_app, moderator_user):
    """Create JWT auth headers for moderator requests."""
    additional_claims = {
        'username': moderator_user.username,
        'email': moderator_user.email,
        'picture': moderator_user.profile_pic
    }
    access_token = create_access_token(
        identity=str(moderator_user.id),
        additional_claims=additional_claims
    )
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def moderator_authenticated_client(test_app, moderator_auth_headers):
    """Create a test client wrapper with moderator auth."""
    client = test_app.test_client()
    return AuthenticatedClient(client, moderator_auth_headers)
