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
