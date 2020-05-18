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
        data = [row._asdict() for row in monthlyReve]
        return json.dumps(data)


class handleEPSFP(MethodView):
    def get(self, stock_id):
        EPS = db.session\
            .query()\
            .with_entities(
                Income_Sheet.year,
                Income_Sheet.season,
                Income_Sheet.基本每股盈餘)\
            .filter_by(stock_id=stock_id)\
            .order_by(Income_Sheet.year.desc())\
            .order_by(Income_Sheet.season.desc())\
            .limit(20).all()
        data = [row._asdict() for row in EPS]
        return json.dumps(data)


class handleDailyInfo(MethodView):
    def get(self, stock_id):
        dailyInfo = db.session\
            .query()\
            .with_entities(
                Daily_Information.本日收盤價,
                Daily_Information.本日漲跌,
                Daily_Information.本益比,
                Daily_Information.近四季每股盈餘)\
            .filter_by(stock_id=stock_id)\
            .one_or_none()
        # dailyInfo = list(dailyInfo)
        data = [row._asdict() for row in [dailyInfo]]
        return json.dumps(data)


class handleIncomeSheet(MethodView):
    def get(self, stock_id):
        incomeSheet = db.session\
            .query()\
            .with_entities(
                Income_Sheet.year,
                Income_Sheet.season,
                Income_Sheet.營業收入合計,
                Income_Sheet.營業毛利,
                Income_Sheet.營業利益,
                Income_Sheet.稅前淨利,
                Income_Sheet.本期淨利,
                Income_Sheet.母公司業主淨利)\
            .filter_by(stock_id=stock_id)\
            .order_by(Income_Sheet.year.desc())\
            .order_by(Income_Sheet.season.desc())\
            .limit(20).all()
        data = [row._asdict() for row in incomeSheet]
        return json.dumps(data)


class handleProfitAnalysis(MethodView):
    def get(self, stock_id):
        profit = db.session\
            .query()\
            .with_entities(
                Income_Sheet.year,
                Income_Sheet.season,
                Income_Sheet.營業毛利率,
                Income_Sheet.營業利益率,
                Income_Sheet.稅前淨利率,
                Income_Sheet.本期淨利率)\
            .filter_by(stock_id=stock_id)\
            .order_by(Income_Sheet.year.desc())\
            .order_by(Income_Sheet.season.desc())\
            .limit(20).all()
        data = [row._asdict() for row in profit]
        return json.dumps(data)


class handleOperationExpenseAnalysis(MethodView):
    def get(self, stock_id):
        operationExpense = db.session\
            .query()\
            .with_entities(
                Income_Sheet.year,
                Income_Sheet.season,
                Income_Sheet.營業費用率,
                Income_Sheet.推銷費用率,
                Income_Sheet.管理費用率,
                Income_Sheet.研究發展費用率,
                Income_Sheet.營業費用,
                Income_Sheet.推銷費用,
                Income_Sheet.管理費用,
                Income_Sheet.研究發展費用)\
            .filter_by(stock_id=stock_id)\
            .order_by(Income_Sheet.year.desc())\
            .order_by(Income_Sheet.season.desc())\
            .limit(20).all()
        data = [row._asdict() for row in operationExpense]
        return json.dumps(data)


# Frontend APIs
frontend.add_url_rule('/month_revenue/<stock_id>',
                      'handleRevenueFP',
                      view_func=handleRevenueFP.as_view(
                        'handleRevenueFP'),
                      methods=['GET'])

frontend.add_url_rule('/eps/<stock_id>',
                      'handleEPSFP',
                      view_func=handleEPSFP.as_view(
                        'handleEPSFP'),
                      methods=['GET'])

frontend.add_url_rule('/daily_info/<stock_id>',
                      'handleDailyInfo',
                      view_func=handleDailyInfo.as_view(
                        'handleDailyInfo'),
                      methods=['GET'])

frontend.add_url_rule('/income_sheet/<stock_id>',
                      'handleIncomeSheet',
                      view_func=handleIncomeSheet.as_view(
                        'handleIncomeSheet'),
                      methods=['GET'])

frontend.add_url_rule('/profit_analysis/<stock_id>',
                      'handleProfitAnalysis',
                      view_func=handleProfitAnalysis.as_view(
                        'handleProfitAnalysis'),
                      methods=['GET'])

frontend.add_url_rule('/op_expense_analysis/<stock_id>',
                      'handleOperationExpenseAnalysis',
                      view_func=handleOperationExpenseAnalysis.as_view(
                        'handleOperationExpenseAnalysis'),
                      methods=['GET'])