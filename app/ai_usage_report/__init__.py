from flask import Blueprint

ai_usage_report = Blueprint('ai_usage_report', __name__)

from . import views  # noqa: E402, F401
