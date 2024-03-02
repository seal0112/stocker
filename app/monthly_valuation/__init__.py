from flask import Blueprint

monthly_valuation = Blueprint('monthly_valuation', __name__)

from . import view