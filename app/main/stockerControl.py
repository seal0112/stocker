from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import (
    Basic_Information, Month_Revenue, Income_Sheet,
    Balance_Sheet, Cash_Flow, Daily_Information,
    Stock_Commodity, Feed, FeedTag
)
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
import json
import math
from datetime import datetime, timezone
from .. import db
from . import main

logger = logging.getLogger()
BASIC_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
DATE_FORMAT = '%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

optionWord = {
    'bullish': '偏多',
    'bearish': '偏空',
    'revenue': '營收整理'
}


def showMain():
    """
    This is the summary defined in yaml file
    First line is the summary
    All following lines until the hyphens is added to description
    the format of the first lines until 3 hyphens will be not yaml compliant
    but everything below the 3 hyphens should be.
    ---
    tags:
      - main page for test
    responses:
      200:
        description: a 2330 daily information
        schema:
          id: Daily_information
          type: array
          properties:
            stock_id:
              default: '2330'
              type: string
          update_date:
            type: string
            default: 'Mon, 1 Jan 2013 00:00:00 GMT'
          本日收盤價:
            type: number
            default: 0
          本日漲跌:
            type: number
            default: 0
          本益比:
            type: number
            default: 0
          近四季每股盈餘:
            type: number
            default: 0
    """
    # try:
    #     tagName = ['財報', '財務報表']
    #     tags = []
    #     for name in tagName:
    #         print(name)
    #         tag = db.session.query(FeedTag).filter_by(
    #             name=name).one_or_none()
    #         if tag == None:
    #             tags.append(FeedTag(name=name))
    #         else:
    #             tags.append(tag)

    #     feed = Feed()
    #     feed.stock_id = '1101'
    #     feed.dateTime= '2021-04-19T12:57:34'
    #     feed.title = '我用台泥測試新的功能'
    #     feed.link = 'https://link.lasd.com/asd/dasdsda?aaa=123'
    #     for tag in tags:
    #         feed.tags.append(tag)

    #     db.session.add(tag, feed)
    #     db.session.commit()
    # except Exception as ex:
    #     print(ex)
    #     db.session.rollback()
    feed = Feed.query.filter_by(
        stock_id='1101',
        title='本公司受邀參加「2021年元大金控線上亞洲投資創富論壇」',
        releaseTime='2021-06-04 12:23:54').one_or_none()

    return jsonify(feed)


@main.route('recommended_stocks')
def getRecommendedStocks():
    """
    Discription:
        this api is used to get recommended stocks.
    Detail:
        According to the received query string option and webhook,
        use option to detemine which SQL syntax should be executed,
        and used webhook to send line notify message.
    Return:
        send message to line notify via webhook.
    Raises:
        Exception: An error occurred.
    """
    option = request.args.get('option')
    webhook = request.args.get('webhook')
    from string import Template
    with open('./critical_file/sqlSyntax.json') as sqlReader:
        sqlSyntax = json.loads(sqlReader.read())

    now = datetime.now()
    season = (math.ceil(now.month/3)-2) % 4 + 1
    year = now.year-1 if season == 4 else now.year
    date = now.strftime('%Y-%m-%d')

    template = Template(sqlSyntax[option])
    sqlCommand = template.substitute(year=year, season=season, date=date)
    results = db.engine.execute(sqlCommand).fetchall()

    if len(results) <= 0:
        return f'No recommended {option} stocks'
    else:
        payload = {
            "message": "{} {}年Q{}{}".format(
                date, year, season, optionWord[option])
        }

        notifyUrl = 'https://notify-api.line.me/api/notify'
        headers = {
            'Authorization': f'Bearer {webhook}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        count = 0
        page = 2
        for result in results:
            payload['message'] += '\n{} EPS:{} YOY:{}% 本益比:{}'.format(
                result[0], result[1], result[2], result[3])
            count += 1

            if count == 10:
                requests.post(notifyUrl, headers=headers, data=payload)
                count = 0
                payload['message'] = "{} {} 第{}頁".format(
                    date, optionWord[option], page) + payload
                page += 1

        try:
            if len(payload) > 0:
                requests.post(notifyUrl, headers=headers, data=payload)
            return 'OK'
        except Exception as ex:
            return make_response(
                json.dumps(str(ex)), 500)


@main.route('revenue_notify')
def sendRevenueNotify():
    """
    This is the summary defined in yaml file
    First line is the summary
    All following lines until the hyphens is added to description
    the format of the first lines until 3 hyphens will be not yaml compliant
    but everything below the 3 hyphens should be.
    """
    option = request.args.get('option')
    webhook = request.args.get('webhook')
    monthList = [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        (10, 11, 12)
    ]
    from string import Template
    with open('./critical_file/sqlSyntax.json') as sqlReader:
        sqlSyntax = json.loads(sqlReader.read())

    now = datetime.now()

    if now.month == 1:
        month = 12
        year = now.year - 1
        season = 4
    else:
        month = now.month - 1
        year = now.year
        season = math.ceil(month/4)
    date = now.strftime('%Y-%m-%d')

    template = Template(sqlSyntax[option])
    sqlCommand = template.substitute(
        year=year, month=month, season=season,
        monthList=monthList[season-1], date=date)
    results = db.engine.execute(sqlCommand).fetchall()

    if len(results) <= 0:
        return f'No recommended {option} stocks'
    else:
        payload = {
            "message": "{} {}年{}月 {}".format(
                date, year, month, optionWord[option])
        }

        notifyUrl = 'https://notify-api.line.me/api/notify'
        headers = {
            'Authorization': f'Bearer {webhook}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        count = 0
        page = 2
        for result in results:
            payload['message'] += '\n{} YOY:{}% 本益比:{}%'.format(
                result[0], result[1], result[2])
            count += 1

            if count == 10:
                requests.post(notifyUrl, headers=headers, data=payload)
                count = 0
                payload['message'] = (
                    "{} {} 第{}頁".format(date, optionWord[option], page)
                )
                page += 1

        try:
            if len(payload) > 0:
                requests.post(notifyUrl, headers=headers, data=payload)
            return 'OK'
        except Exception as ex:
            return make_response(
                json.dumps(str(ex)), 500)


class getStockNumber(MethodView):
    decorators = []

    def get(self):
        companyType = request.args.get('type')
        if companyType is None:
            stockNum = db.session.query(Basic_Information.id).all()
        else:
            stockNum = db.session.query(
                Basic_Information.id).filter_by(exchangeType=companyType).all()
        res = [i[0] for i in stockNum]

        return jsonify(res)

    def post(self):
        payload = json.loads(request.data)
        reportTypeSet = set(["balance_sheet", "income_sheet", "cashflow"])
        try:
            if payload['reportType'] not in reportTypeSet:
                raise KeyError
            reportType = payload['reportType']
            if reportType == 'balance_sheet':
                stockNums = db.session.query(Balance_Sheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'income_sheet':
                stockNums = db.session.query(Income_Sheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'cashflow':
                stockNums = db.session.query(Cash_Flow.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            res = [i[0] for i in stockNums]
        except Exception as ex:
            if ex == KeyError:
                logger.warning(
                    "400 report type %s not found." % (reportType))
                res = make_response(
                    json.dumps('Failed to fetch stock number'), 400)
            else:
                print(ex)
                logger.warning(
                    "400 stock id not found. Reason: %s" % (ex))
                res = make_response(
                    json.dumps(
                        'Failed to update basic_information.'), 400)
            return res

        return jsonify(res)


class handleDailyInfo(MethodView):
    def get(self, stock_id):
        """
        GET stock's daily information
        swagger_from_file: DailyInfo_get.yml
        """
        dailyInfo = db.session.query(Daily_Information).filter_by(
            stock_id=stock_id).one_or_none()

        if dailyInfo is None:
            res = make_response(json.dumps(
                'Failed to get %s Daily information.' % (stock_id)), 404)
            return res
        else:
            return jsonify(dailyInfo.serialize)

    def post(self, stock_id):
        """
        Create or Update stock_id's daily information
        swagger_from_file: DailyInfo_post.yml
        """
        payload = json.loads(request.data)
        dailyInfo = db.session.query(Daily_Information).filter_by(
            stock_id=stock_id).one_or_none()
        try:
            if dailyInfo is not None:
                for key in payload:
                    dailyInfo[key] = payload[key]
                    dailyInfo['update_date'] = datetime.now(
                        ).strftime("%Y-%m-%d")
            else:
                dailyInfo = Daily_Information()
                dailyInfo['stock_id'] = stock_id
                for key in payload:
                    dailyInfo[key] = payload[key]

            dailyInfo.updatePE()

            db.session.add(dailyInfo)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Daily price. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Daily price.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print(ex)
            logger.warning(
                "400 %s is failed to update Daily Information. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Daily Information.'
                    % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('OK'), 200)
        return res


class handleStockCommodity(MethodView):
    """
    Description:
        this api is used to handle Stock Commodity request.
    Detail:
        According to the received stock_id and request method(GET/POST),
        if request method is GET, then return stock_id's Commodity.
        if request method is POST, then according to the data entered,
        decide whether to update or add new commodity into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's commodity.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred then return 400.
    """

    def get(self, stock_id):
        stockCommodity = db.session.query(Stock_Commodity).filter_by(
            stock_id=stock_id).one_or_none()
        return 'Stock Commodity: %s' % stock_id\
            if stockCommodity is None else stockCommodity.serialize

    def post(self, stock_id):
        payload = json.loads(request.data)
        stockCommodity = db.session.query(Stock_Commodity).filter_by(
            stock_id=stock_id).one_or_none()
        try:
            if stockCommodity is not None:
                for key in payload:
                    stockCommodity[key] = payload[key]
            else:
                stockCommodity = Stock_Commodity()
                stockCommodity['stock_id'] = stock_id
                for key in payload:
                    stockCommodity[key] = payload[key]

            db.session.add(stockCommodity)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Stock Commodity. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Stock Commodity.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print(ex)
            logger.warning(
                "400 %s is failed to update Stock Commodity. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Stock Commodity.'
                    % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('OK'), 200)
        return res


main.add_url_rule('/',
                  'showMain',
                  view_func=showMain)
main.add_url_rule('/stock_number',
                  'getStockNumber',
                  view_func=getStockNumber.as_view(
                      'getStockNumber_api'),
                  methods=['GET', 'POST'])
main.add_url_rule('/daily_information/<stock_id>',
                  'handleDailyInfo',
                  view_func=handleDailyInfo.as_view(
                      'handleDailyInfo'),
                  methods=['GET', 'POST'])
main.add_url_rule('/stock_commodity/<stock_id>',
                  'handleStockCommodity',
                  view_func=handleStockCommodity.as_view(
                      'handleStockCommodity'),
                  methods=['GET', 'POST'])
