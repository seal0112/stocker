from flask import Blueprint

recommended_stock = Blueprint('recommended_stock', __name__)

from . import view
