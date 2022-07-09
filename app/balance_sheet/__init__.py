from flask import Blueprint

balance_sheet = Blueprint('balance_sheet', __name__)

from . import view
