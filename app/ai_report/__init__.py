from flask import Blueprint

ai_report = Blueprint('ai_report', __name__)

from . import views
