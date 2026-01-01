from flask import Blueprint

user_management = Blueprint('user_management', __name__)
roles_bp = Blueprint('roles', __name__)

from . import views  # noqa: F401, E402
