from flask import Blueprint

ai_api_key = Blueprint('ai_api_key', __name__)

from . import views  # noqa: E402, F401
