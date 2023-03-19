from flask import Blueprint

follow_stock = Blueprint('follow_stock', __name__)

from . import view
