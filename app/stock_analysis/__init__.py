from flask import Blueprint

stock_analysis = Blueprint('stock_analysis', __name__)

from . import views  # noqa: E402, F401
