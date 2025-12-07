from datetime import datetime, timezone

from app import db


class UserRole(db.Model):
    """
    Association model for User-Role many-to-many relationship.
    Using a model instead of db.Table allows adding extra fields.
    """
    __tablename__ = 'user_role'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    # Relationships (viewonly to avoid conflicts with User.roles and Role.users)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('user_roles', lazy='dynamic'), viewonly=True)
    role = db.relationship('Role', backref=db.backref('role_users', lazy='dynamic'), viewonly=True)
    assigner = db.relationship('User', foreign_keys=[assigned_by], viewonly=True)

    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>'

    @property
    def is_expired(self):
        """Check if the role assignment has expired."""
        if self.expires_at is None:
            return False
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return now > self.expires_at

    @property
    def is_active(self):
        """Check if the role assignment is currently active (not expired)."""
        return not self.is_expired
