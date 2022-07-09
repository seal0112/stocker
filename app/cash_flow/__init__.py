from flask import Blueprint

cash_flow = Blueprint('cash_flow', __name__)

from . import view
