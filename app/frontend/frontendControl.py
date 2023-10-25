import logging
import json
import pytz
import re
from datetime import datetime, timedelta

from flask import request, jsonify, make_response
from sqlalchemy.sql import func
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import frontend
from .. import db
from ..database_setup import (
    Basic_Information, Month_Revenue, Income_Sheet,
    Daily_Information, Stock_Commodity, Feed, StockSearchCounts
)
from ..utils.stock_search_count_service import StockSearchCountService

logger = logging.getLogger()
stock_search_count_service = StockSearchCountService()


@frontend.route('/stock_info_commodity/<stock_id>')
@jwt_required()
def getFrontEndStockInfoAndCommodity(stock_id):
    current_user = get_jwt_identity()
    stock_search_count_service.increase_stock_search_count(current_user['email'], stock_id)
    resData = {}

    stockInfo = db.session\
        .query()\
        .with_entities(
            Basic_Information.公司簡稱,
            Basic_Information.產業類別,
            Basic_Information.exchange_type)\
        .filter_by(id=stock_id)\
        .one_or_none()
    if stockInfo == None:
        res = make_response(
                json.dumps("Couldn't find stock: {}".format(stock_id)), 404)
        return res
    else:
        infoData = stockInfo._asdict()
    resData['stockInformation'] = infoData

    stockCommo = db.session\
        .query()\
        .with_entities(
            Stock_Commodity.stock_future,
            Stock_Commodity.stock_option,
            Stock_Commodity.small_stock_future,)\
        .filter_by(stock_id=stock_id)\
        .one_or_none()

    if stockCommo is None:
        commoData = {
            'stock_future': False,
            'stock_option': False,
            'small_stock_future': False
        }
    else:
        commoData = stockCommo._asdict()
    resData['stockCommodity'] = commoData

    return jsonify(resData)


@frontend.route('/check_stock_exist/<stock_id>')
@jwt_required()
def checkStockExist(stock_id):
    stockInfo = db.session\
        .query(Basic_Information)\
        .filter_by(id=stock_id)\
        .one_or_none()
    if stockInfo == None:
        res = make_response(
                json.dumps("Couldn't find stock: {}".format(stock_id)), 404)
        return res
    else:
        res = make_response(
                json.dumps("stock exist: {}".format(stock_id)), 200)
        return res


@frontend.route('/daily_info/<stock_id>')
@jwt_required()
def getFrontEndDailyInfo(stock_id):
    dailyInfo = db.session\
        .query()\
        .with_entities(
            Daily_Information.本日收盤價,
            Daily_Information.本日漲跌,
            Daily_Information.本益比,
            Daily_Information.近四季每股盈餘,
            Daily_Information.殖利率,
            Daily_Information.股價淨值比)\
        .filter_by(stock_id=stock_id)\
        .one_or_none()
    if dailyInfo == None:
        res = make_response(
                json.dumps("Couldn't find stock: {}".format(stock_id)), 404)
        return res
    else:
        data = dailyInfo._asdict()
        return jsonify(data)


@frontend.route('/month_revenue/<stock_id>')
@jwt_required()
def getFrontEndMonthRevenue(stock_id):
    monthlyReve = db.session\
        .query()\
        .with_entities(
            func.concat(
                Month_Revenue.year, '/', Month_Revenue.month).label(
                    "Year/Month"),
            Month_Revenue.當月營收,
            Month_Revenue.去年同月增減,
            Month_Revenue.上月比較增減)\
        .filter_by(stock_id=stock_id)\
        .filter(Month_Revenue.year >= datetime.now().year-5)\
        .order_by(Month_Revenue.year.desc())\
        .order_by(Month_Revenue.month.desc())\
        .all()
    data = [row._asdict() for row in monthlyReve][::-1]
    return jsonify(data)


@frontend.route('/eps/<stock_id>')
@jwt_required()
def getFrontEndEPS(stock_id):
    EPS = db.session\
        .query()\
        .with_entities(
            func.concat(
                Income_Sheet.year, 'Q', Income_Sheet.season).label(
                    "Year/Season"),
            Income_Sheet.基本每股盈餘)\
        .filter_by(stock_id=stock_id)\
        .filter(Income_Sheet.year >= datetime.now().year-5)\
        .order_by(Income_Sheet.year.desc())\
        .order_by(Income_Sheet.season.desc())\
        .all()
    data = [row._asdict() for row in EPS][::-1]
    return jsonify(data)


@frontend.route('/income_sheet/<stock_id>')
@jwt_required()
def getFrontEndIncomeSheet(stock_id):
    incomeSheet = db.session\
        .query()\
        .with_entities(
            func.concat(
                Income_Sheet.year, 'Q', Income_Sheet.season).label(
                    "Year/Season"),
            Income_Sheet.營業收入合計,
            Income_Sheet.營業毛利,
            Income_Sheet.營業利益,
            Income_Sheet.稅前淨利,
            Income_Sheet.本期淨利,
            Income_Sheet.母公司業主淨利)\
        .filter_by(stock_id=stock_id)\
        .filter(Income_Sheet.year >= datetime.now().year-5)\
        .order_by(Income_Sheet.year.desc())\
        .order_by(Income_Sheet.season.desc())\
        .all()
    data = [row._asdict() for row in incomeSheet][::-1]
    return jsonify(data)


@frontend.route('/profit_analysis/<stock_id>')
@jwt_required()
def getFrontEndProfitAnalysis(stock_id):
    profit = db.session\
        .query()\
        .with_entities(
            func.concat(
                Income_Sheet.year, 'Q', Income_Sheet.season).label(
                    "Year/Season"),
            Income_Sheet.營業毛利率,
            Income_Sheet.營業利益率,
            Income_Sheet.稅前淨利率,
            Income_Sheet.本期淨利率)\
        .filter_by(stock_id=stock_id)\
        .filter(Income_Sheet.year >= datetime.now().year-5)\
        .order_by(Income_Sheet.year.desc())\
        .order_by(Income_Sheet.season.desc())\
        .all()
    data = [row._asdict() for row in profit][::-1]
    return jsonify(data)


@frontend.route('/op_expense_analysis/<stock_id>')
@jwt_required()
def getFrontEndOperationExpenseAnalysis(stock_id):
    operationExpense = db.session\
        .query()\
        .with_entities(
            func.concat(
                Income_Sheet.year, 'Q', Income_Sheet.season).label(
                    "Year/Season"),
            Income_Sheet.營業費用率,
            Income_Sheet.推銷費用率,
            Income_Sheet.管理費用率,
            Income_Sheet.研究發展費用率,
            Income_Sheet.營業費用,
            Income_Sheet.推銷費用,
            Income_Sheet.管理費用,
            Income_Sheet.研究發展費用)\
        .filter_by(stock_id=stock_id)\
        .filter(Income_Sheet.year >= datetime.now().year-5)\
        .order_by(Income_Sheet.year.desc())\
        .order_by(Income_Sheet.season.desc())\
        .all()
    data = [row._asdict() for row in operationExpense][::-1]
    return jsonify(data)


@frontend.route('/feed')
@jwt_required()
def getMarketFeed():
    target_date = request.args.get('targetDate')
    feed_type = request.args.get('feedType')
    page = request.args.get('page', 0)
    page_size = request.args.get('page_size', 5)
    start_time = datetime.strptime(target_date, '%Y-%m-%d').astimezone(tz=pytz.UTC)
    end_time = datetime.strptime(target_date, '%Y-%m-%d') + timedelta(days=1)
    feed_query = Feed.query.filter(
        Feed.releaseTime.between(start_time, end_time)).order_by(
            Feed.releaseTime.desc())

    if feed_type != 'all':
        feed_query = feed_query.filter_by(feedType=feed_type)

    feeds = feed_query.paginate(
        page=int(page), per_page=int(page_size), error_out=False)

    return jsonify({
        'feeds': [feed.serialize for feed in feeds],
        'next_page': feeds.next_num,
        'has_next': feeds.has_next
    })


@frontend.route('/autocomplete')
@jwt_required()
def getStockAutocomplete():
    search_stock = request.args.get('search_stock')

    if search_stock is None:
        return jsonify({ 'stocks': [] })

    if re.search("^[0-9]{1,4}$", search_stock):
        subq = Basic_Information.query.filter(
            Basic_Information.id.like(f'{search_stock}%'))
    else:
        subq = Basic_Information.query.filter(
            Basic_Information.公司簡稱.like(f'{search_stock}%'))

    subq = subq.with_entities(Basic_Information.id, Basic_Information.公司簡稱).subquery()

    stock_list = StockSearchCounts.query.join(
        subq, StockSearchCounts.stock_id == subq.c.id).order_by(
            StockSearchCounts.search_count.desc()).with_entities(subq.c.id, subq.c.公司簡稱).limit(8).all()

    return jsonify([
        {
            'stock': stock[0],
            'name': stock[1]
        } for stock in stock_list
    ])
