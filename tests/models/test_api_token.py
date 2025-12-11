"""Unit tests for ApiToken model."""
import pytest
from datetime import datetime, timedelta

from app import db
from app.models import ApiToken, User
from app.models.role import Role


@pytest.fixture
def test_user(test_app):
    """Create a test user for token tests."""
    # Ensure user role exists
    role = Role.query.filter_by(name='user').first()
    if not role:
        role = Role(name='user', description='Regular User', is_default=True)
        db.session.add(role)
        db.session.commit()

    user = User(
        username='token_test_user',
        email='token_test@test.com',
        active=True,
        authenticate=True
    )
    user.set_password('testpassword123')
    user.roles.append(role)
    db.session.add(user)
    db.session.commit()

    yield user

    # Cleanup - delete tokens first, then user
    ApiToken.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()


class TestApiTokenModel:
    """Tests for ApiToken model."""

    def test_generate_token_format(self, test_app):
        """Generated token should have correct format."""
        token = ApiToken.generate_token()
        assert token.startswith('stk_')
        assert len(token) == 4 + 32  # prefix + 32 hex chars

    def test_hash_token_returns_sha256(self, test_app):
        """Token should be hashed with SHA256."""
        token = 'stk_abc123'
        token_hash = ApiToken.hash_token(token)
        assert len(token_hash) == 64  # SHA256 produces 64 hex chars

    def test_hash_token_is_deterministic(self, test_app):
        """Same token should produce same hash."""
        token = 'stk_abc123'
        hash1 = ApiToken.hash_token(token)
        hash2 = ApiToken.hash_token(token)
        assert hash1 == hash2

    def test_get_token_prefix(self, test_app):
        """Token prefix should be first 12 characters."""
        token = 'stk_abc123def456'
        prefix = ApiToken.get_token_prefix(token)
        assert prefix == 'stk_abc12345'

    def test_create_token_success(self, test_app, test_user):
        """Creating a token should return ApiToken and plain token."""
        api_token, plain_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Test Token'
        )

        assert api_token is not None
        assert api_token.id is not None
        assert api_token.name == 'Test Token'
        assert api_token.user_id == test_user.id
        assert api_token.is_active is True
        assert plain_token.startswith('stk_')

    def test_create_token_with_scopes(self, test_app, test_user):
        """Creating a token with scopes should store them."""
        api_token, _ = ApiToken.create_token(
            user_id=test_user.id,
            name='Scoped Token',
            scopes=['read', 'write']
        )

        assert api_token.scopes == ['read', 'write']

    def test_create_token_with_expiration(self, test_app, test_user):
        """Creating a token with expiration should set expires_at."""
        expires = datetime.utcnow() + timedelta(days=30)
        api_token, _ = ApiToken.create_token(
            user_id=test_user.id,
            name='Expiring Token',
            expires_at=expires
        )

        assert api_token.expires_at is not None
        assert api_token.expires_at.date() == expires.date()

    def test_create_token_max_limit(self, test_app, test_user):
        """Creating more than MAX_TOKENS_PER_USER should raise error."""
        # Create max tokens
        for i in range(ApiToken.MAX_TOKENS_PER_USER):
            ApiToken.create_token(user_id=test_user.id, name=f'Token {i}')

        # Try to create one more
        with pytest.raises(ValueError, match='Maximum .* tokens allowed'):
            ApiToken.create_token(user_id=test_user.id, name='Extra Token')

    def test_verify_token_success(self, test_app, test_user):
        """Valid token should be verified successfully."""
        api_token, plain_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Verify Token'
        )

        verified = ApiToken.verify_token(plain_token)
        assert verified is not None
        assert verified.id == api_token.id

    def test_verify_token_invalid(self, test_app):
        """Invalid token should return None."""
        verified = ApiToken.verify_token('stk_invalid_token_123')
        assert verified is None

    def test_verify_token_wrong_prefix(self, test_app):
        """Token with wrong prefix should return None."""
        verified = ApiToken.verify_token('wrong_prefix_123')
        assert verified is None

    def test_verify_token_expired(self, test_app, test_user):
        """Expired token should return None."""
        expires = datetime.utcnow() - timedelta(days=1)  # Already expired
        api_token, plain_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Expired Token',
            expires_at=expires
        )

        verified = ApiToken.verify_token(plain_token)
        assert verified is None

    def test_verify_token_updates_last_used(self, test_app, test_user):
        """Verifying a token should update last_used_at."""
        api_token, plain_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Last Used Token'
        )

        assert api_token.last_used_at is None

        ApiToken.verify_token(plain_token)
        db.session.refresh(api_token)

        assert api_token.last_used_at is not None

    def test_revoke_token(self, test_app, test_user):
        """Revoking a token should set is_active to False."""
        api_token, plain_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Revoke Token'
        )

        assert api_token.is_active is True

        api_token.revoke()

        assert api_token.is_active is False

        # Verify token should fail after revoke
        verified = ApiToken.verify_token(plain_token)
        assert verified is None

    def test_regenerate_token(self, test_app, test_user):
        """Regenerating a token should create new token value."""
        api_token, old_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Regenerate Token'
        )

        old_hash = api_token.token_hash

        new_token = api_token.regenerate()

        assert new_token != old_token
        assert api_token.token_hash != old_hash
        assert new_token.startswith('stk_')

        # Old token should not work
        assert ApiToken.verify_token(old_token) is None

        # New token should work
        assert ApiToken.verify_token(new_token) is not None

    def test_is_expired_property(self, test_app, test_user):
        """is_expired property should work correctly."""
        # Token without expiration
        api_token1, _ = ApiToken.create_token(
            user_id=test_user.id,
            name='No Expiry Token'
        )
        assert api_token1.is_expired is False

        # Token with future expiration
        api_token2, _ = ApiToken.create_token(
            user_id=test_user.id,
            name='Future Token',
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        assert api_token2.is_expired is False

    def test_to_dict(self, test_app, test_user):
        """to_dict should return correct dictionary."""
        api_token, plain_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Dict Token',
            scopes=['read']
        )

        result = api_token.to_dict()

        assert result['id'] == api_token.id
        assert result['name'] == 'Dict Token'
        assert result['token_prefix'] == api_token.token_prefix
        assert result['scopes'] == ['read']
        assert result['is_active'] is True
        assert 'token' not in result

    def test_to_dict_with_token(self, test_app, test_user):
        """to_dict with include_token should include plain token."""
        api_token, plain_token = ApiToken.create_token(
            user_id=test_user.id,
            name='Dict Token With Plain'
        )

        result = api_token.to_dict(include_token=True, plain_token=plain_token)

        assert result['token'] == plain_token
