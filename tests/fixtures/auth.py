"""Authentication fixtures for API tests."""
import pytest
from flask_jwt_extended import create_access_token


@pytest.fixture
def auth_headers(test_app, regular_user):
    """Create JWT auth headers for authenticated requests."""
    identity = {
        'id': regular_user.id,
        'username': regular_user.username,
        'email': regular_user.email,
        'picture': regular_user.profile_pic
    }
    access_token = create_access_token(identity=identity)
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def authenticated_client(test_app, auth_headers):
    """Create a test client wrapper that includes auth headers in all requests."""
    client = test_app.test_client()

    class AuthenticatedClient:
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

    return AuthenticatedClient(client, auth_headers)
