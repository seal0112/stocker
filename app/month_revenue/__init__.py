from flask import Blueprint

month_revenue = Blueprint('month_revenue', __name__)

from . import view
