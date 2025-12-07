from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True, index=True)
    profile_pic = db.Column(db.String(512))
    external_type = db.Column(db.String(16))
    external_id = db.Column(db.String(64))
    authenticate = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # Many-to-many relationship with Role (via UserRole model)
    roles = db.relationship(
        'Role',
        secondary='user_role',
        primaryjoin='User.id == foreign(UserRole.user_id)',
        secondaryjoin='Role.id == foreign(UserRole.role_id)',
        backref=db.backref('users', lazy='dynamic'),
        lazy='joined'
    )

    def __repr__(self):
        return f'<{self.id} User {self.username}>'

    def set_password(self, password):
        """Create hashed password."""
        print(password)
        self.password_hash = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return self.authenticate

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return self.id
        except AttributeError as ex:
            raise NotImplementedError(
                'No `id` attribute - override `get_id`') from ex

    def has_role(self, role_name):
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)

    def add_role(self, role):
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role):
        """Remove a role from the user. Default user role cannot be removed."""
        if role.name == 'user':
            raise ValueError("Cannot remove user role")
        if role in self.roles:
            self.roles.remove(role)

    def assign_default_role(self):
        """Assign the default role to this user if they have no roles."""
        if not self.roles:
            from app.models.role import Role
            default_role = Role.get_default_role()
            if default_role:
                self.roles.append(default_role)

    @property
    def role_names(self):
        """Get list of role names."""
        return [role.name for role in self.roles]

    def has_permission(self, permission_name):
        """Check if user has a specific permission through any of their roles."""
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False

    @property
    def permissions(self):
        """Get all permissions from all roles."""
        if self.has_role('admin'):
            return ['*']
        perms = set()
        for role in self.roles:
            for p in role.permissions:
                perms.add(p.name)
        return list(perms)
