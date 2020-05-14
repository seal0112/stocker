from flask import Flask, request, redirect, url_for
from flask import jsonify, make_response, render_template
from flask import Blueprint
from flask.views import MethodView
from ..database_setup import (
    Basic_Information, Month_Revenue, Income_Sheet,
    Balance_Sheet, Cash_Flow, Daily_Information,
    Stock_Commodity
)
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import datetime
from . import frontend
from .. import db

# logger = logging.getLogger()
# BASIC_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
# DATE_FORMAT = '%m-%d %H:%M'
# formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(formatter)
# logger.addHandler(console)


class handleRevenueFP(MethodView):
    def get(self, stock_id):
        monthlyReve = db.session\
            .query()\
            .with_entities(
                Month_Revenue.year,
                Month_Revenue.month,
                Month_Revenue.當月營收,
                Month_Revenue.去年同月增減)\
            .filter_by(stock_id=stock_id)\
            .order_by(Month_Revenue.year.desc())\
            .order_by(Month_Revenue.month.desc())\
            .limit(60).all()
        return json.dumps(monthlyReve)

# Frontend APIs
frontend.add_url_rule('/month_revenue/<stock_id>',
                 'handleRevenueFP',
                 view_func=handleRevenueFP.as_view(
                     'handleRevenueFP'),
                 methods=['GET'])
