from flask import Blueprint

api_token = Blueprint('api_token', __name__)

from . import views
