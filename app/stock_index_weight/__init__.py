from flask import Blueprint

stock_index_weight = Blueprint('stock_index_weight', __name__)

from . import view
