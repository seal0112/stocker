from datetime import datetime, timedelta

from app.models import ApiToken


class TokenService:
    """Service for managing API tokens."""

    def get_user_tokens(self, user_id, include_inactive=False):
        """Get all tokens for a user."""
        query = ApiToken.query.filter_by(user_id=user_id)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(ApiToken.created_at.desc()).all()

    def get_token_by_id(self, token_id, user_id=None):
        """Get a specific token by ID, optionally filtered by user."""
        query = ApiToken.query.filter_by(id=token_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()

    def create_token(self, user_id, name, scopes=None, expires_in_days=None):
        """
        Create a new API token.
        Returns tuple of (ApiToken, plain_token).
        """
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        return ApiToken.create_token(
            user_id=user_id,
            name=name,
            scopes=scopes,
            expires_at=expires_at
        )

    def revoke_token(self, token_id, user_id):
        """Revoke a token."""
        token = self.get_token_by_id(token_id, user_id)
        if not token:
            return False
        token.revoke()
        return True

    def regenerate_token(self, token_id, user_id):
        """
        Regenerate a token.
        Returns the new plain token or None if not found.
        """
        token = self.get_token_by_id(token_id, user_id)
        if not token or not token.is_active:
            return None
        return token.regenerate()

    def verify_token(self, token_string):
        """Verify a token string and return the ApiToken if valid."""
        return ApiToken.verify_token(token_string)

    def get_token_count(self, user_id):
        """Get the number of active tokens for a user."""
        return ApiToken.query.filter_by(user_id=user_id, is_active=True).count()

    def can_create_token(self, user_id):
        """Check if user can create more tokens."""
        return self.get_token_count(user_id) < ApiToken.MAX_TOKENS_PER_USER
