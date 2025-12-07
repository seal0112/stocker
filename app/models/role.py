from datetime import datetime, timezone

from app import db


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Many-to-many relationship with Permission
    permissions = db.relationship(
        'Permission',
        secondary='role_permission',
        backref=db.backref('roles', lazy='dynamic'),
        lazy='joined'
    )

    def __repr__(self):
        return f'<Role {self.name}>'

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @classmethod
    def get_default_role(cls):
        """Get the default role for new users."""
        return cls.query.filter_by(is_default=True).first()

    @classmethod
    def set_default_role(cls, role_name):
        """Set a role as the default role. Only one role can be default."""
        # Remove default from all roles
        cls.query.update({cls.is_default: False})
        # Set the specified role as default
        role = cls.query.filter_by(name=role_name).first()
        if role:
            role.is_default = True
            db.session.commit()
            return role
        return None

    def has_permission(self, permission_name):
        """Check if role has a specific permission."""
        # Admin has all permissions
        if self.name == 'admin':
            return True
        return any(p.name == permission_name for p in self.permissions)

    def add_permission(self, permission):
        """Add a permission to this role."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission):
        """Remove a permission from this role."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    @property
    def permission_names(self):
        """Get list of permission names."""
        if self.name == 'admin':
            return ['*']
        return [p.name for p in self.permissions]
