from flask import Blueprint

announcement_income_sheet_analysis = Blueprint('announcement_income_sheet_analysis', __name__)

from . import views
