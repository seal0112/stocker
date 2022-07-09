from flask import Blueprint

income_sheet = Blueprint('income_sheet', __name__)

from . import view
