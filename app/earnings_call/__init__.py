from flask import Blueprint

earnings_call = Blueprint('earnings_call', __name__)

from . import views