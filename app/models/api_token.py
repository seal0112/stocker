import uuid
import secrets
import hashlib
from datetime import datetime

from app import db


class ApiToken(db.Model):
    """Personal Access Token for API authentication."""
    __tablename__ = 'api_token'

    TOKEN_PREFIX = 'stk_'
    TOKEN_LENGTH = 32
    MAX_TOKENS_PER_USER = 3

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    token_prefix = db.Column(db.String(12), nullable=False)  # stk_ + first 8 chars
    scopes = db.Column(db.JSON, default=list)
    expires_at = db.Column(db.DateTime, nullable=True)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('api_tokens', lazy='dynamic'))

    def __repr__(self):
        return f'<ApiToken {self.token_prefix}... ({self.name})>'

    @classmethod
    def generate_token(cls):
        """Generate a new random token string."""
        random_part = secrets.token_hex(cls.TOKEN_LENGTH // 2)
        return f'{cls.TOKEN_PREFIX}{random_part}'

    @classmethod
    def hash_token(cls, token):
        """Hash a token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def get_token_prefix(cls, token):
        """Get the prefix portion of a token for display."""
        return token[:12] if len(token) >= 12 else token

    @classmethod
    def create_token(cls, user_id, name, scopes=None, expires_at=None):
        """
        Create a new API token for a user.
        Returns tuple of (ApiToken instance, plain_token).
        The plain_token is only available at creation time.
        """
        # Check token limit
        token_count = cls.query.filter_by(user_id=user_id, is_active=True).count()
        if token_count >= cls.MAX_TOKENS_PER_USER:
            raise ValueError(f'Maximum {cls.MAX_TOKENS_PER_USER} tokens allowed per user')

        plain_token = cls.generate_token()
        token_hash = cls.hash_token(plain_token)
        token_prefix = cls.get_token_prefix(plain_token)

        api_token = cls(
            user_id=user_id,
            name=name,
            token_hash=token_hash,
            token_prefix=token_prefix,
            scopes=scopes or [],
            expires_at=expires_at
        )

        db.session.add(api_token)
        db.session.commit()

        return api_token, plain_token

    @classmethod
    def verify_token(cls, token):
        """
        Verify a token and return the associated ApiToken if valid.
        Returns None if token is invalid, expired, or inactive.
        """
        if not token or not token.startswith(cls.TOKEN_PREFIX):
            return None

        token_hash = cls.hash_token(token)
        api_token = cls.query.filter_by(token_hash=token_hash, is_active=True).first()

        if not api_token:
            return None

        # Check expiration
        if api_token.expires_at and api_token.expires_at < datetime.utcnow():
            return None

        # Update last used timestamp
        api_token.last_used_at = datetime.utcnow()
        db.session.commit()

        return api_token

    def revoke(self):
        """Revoke this token."""
        self.is_active = False
        db.session.commit()

    def regenerate(self):
        """
        Regenerate this token with a new value.
        Returns the new plain token (only available once).
        """
        plain_token = self.generate_token()
        self.token_hash = self.hash_token(plain_token)
        self.token_prefix = self.get_token_prefix(plain_token)
        self.created_at = datetime.utcnow()
        self.last_used_at = None
        db.session.commit()

        return plain_token

    @property
    def is_expired(self):
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return self.expires_at < datetime.utcnow()

    def to_dict(self, include_token=False, plain_token=None):
        """Convert to dictionary for API response."""
        result = {
            'id': self.id,
            'name': self.name,
            'token_prefix': self.token_prefix,
            'scopes': self.scopes,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

        if include_token and plain_token:
            result['token'] = plain_token

        return result
