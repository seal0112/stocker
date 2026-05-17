from flask import Blueprint
ai_setting = Blueprint('ai_setting', __name__)
from . import views  # noqa: F401, E402
