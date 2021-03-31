from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import (
    Basic_Information, Month_Revenue, Income_Sheet,
    Balance_Sheet, Cash_Flow, Daily_Information,
    Stock_Commodity
)
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
import json
import math
import datetime
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
    checkFourSeasonEPS(2330)
    b = db.session.query(Daily_Information).filter_by(
        stock_id='2330').all()
    res = [i.serialize for i in b]
    return jsonify(res)

@main.route('recommended_stocks')
def getRecommendedStocks():
    """
    This is the summary defined in yaml file
    First line is the summary
    All following lines until the hyphens is added to description
    the format of the first lines until 3 hyphens will be not yaml compliant
    but everything below the 3 hyphens should be.
    """
    option = request.args.get('option')
    webhook = request.args.get('webhook')
    from string import Template
    with open('./critical_file/sqlSyntax.json') as sqlReader:
        sqlSyntax = json.loads(sqlReader.read())

    optionWord = {
        'bullish': '偏多',
        'bearish': '偏空'
    }

    now = datetime.datetime.now()
    season = (math.ceil(now.month/3)-2)%4+1
    year = now.year-1 if season==4 else now.year
    date = now.strftime('%Y-%m-%d')

    template = Template(sqlSyntax[option])
    sqlCommand = template.substitute(year=year, season=season, date=date)
    results = db.engine.execute(sqlCommand).fetchall()

    if len(results) <= 0:
        return f'No recommended {option} stocks'
    else:
        payload = {
            "message": "{} {}年Q{}{}".format(date, year, season, optionWord[option])
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
                payload = "{} {} 第{}頁".format(date, optionWord[option], page) + payload
                requests.post(notifyUrl, headers=headers, data=payload)
                count = 0
                payload['message'] = ""
                page += 1

        try:
            if len(payload) > 0:
                payload = "{} {} 第{}頁".format(date, optionWord[option], page) + payload
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


class handleBasicInfo(MethodView):
    """
    Discription:
        this api is used to handle basic information request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's basic information.
        if request method is POST, then according to the data entered,
        decide whether to update or add new data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's basic information.
        if request method is POST,
            According to whether the data is written into the database.
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        """
        GET stock's basic information
        swagger_from_file: BasicInformation_get.yml
        """
        basicInfo = db.session.query(Basic_Information).filter_by(
            id=stock_id).one_or_none()
        if basicInfo is None:
            return make_response(
                json.dumps("404 Not Found"), 404)
        else:
            return jsonify(basicInfo.serialize)

    def post(self, stock_id):
        """
        Add or Update stock basic information.
        swagger_from_file: BasicInformation_post.yml
        """
        basicInfo = db.session.query(Basic_Information).filter_by(
            id=stock_id).one_or_none()
        try:
            payload = json.loads(request.data)
            if basicInfo is not None:

                # typeConversSet is used to converse datatype from user input.
                typeConversSet = set(("實收資本額", "已發行普通股數或TDR原發行股數",
                                      "私募普通股", "特別股"))
                changeFlag = False
                for key in payload:
                    if key in typeConversSet:
                        payload[key] = int(payload[key])
                    if basicInfo[key] != payload[key]:
                        changeFlag = True
                        basicInfo[key] = payload[key]

                # If no data has been modified, then return 200
                if not changeFlag:
                    return make_response(json.dumps('OK'), 200)

                # If any data is modified,
                # update update_date to today's date
                basicInfo['update_date'] = datetime.datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                basicInfo = Basic_Information()
                for key in payload:
                    basicInfo[key] = payload[key]

            db.session.add(basicInfo)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Basic Info. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Basic Info.' % (stock_id)), 400)
            return res
        except Exception as ex:
            print(ex)
            logger.warning(
                "400 %s is failed to update basic_information. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Basic Info.'), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res

    def patch(self, stock_id):
        """
        Update stock basic information.
        swagger_from_file: BasicInformation_patch.yml
        """
        basicInfo = db.session.query(Basic_Information).filter_by(
            id=stock_id).one_or_none()
        try:
            payload = json.loads(request.data)
            if basicInfo is not None:
                basicInfo['exchangeType'] = payload['exchangeType']
                db.session.add(basicInfo)
                db.session.commit()
                res = make_response(json.dumps('OK'), 200)
            else:
                res = make_response(
                    json.dumps('No such stock id.'), 404)
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
                    dailyInfo['update_date'] = datetime.datetime.now(
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
                "400 %s is failed to update Daily Price. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Daily Price.' % (stock_id)), 400)
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


class handleIncomeSheet(MethodView):
    """
    Description:
        this api is used to handle income sheet request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's income sheet.
        if request method is POST, then according to the data entered,
        decide whether to update or add new income sheet data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's income sheet.
        if request method is POST,
            According to whether the data is written into the database.
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        """
        return stock's Income Sheet with designated Year and season
        swagger_from_file: IncomeSheet_get.yml
        """
        mode = request.args.get('mode')
        if mode is None:
            incomeSheet = db.session.query(Income_Sheet).filter_by(
                stock_id=stock_id).order_by(
                    Income_Sheet.year.desc()).order_by(
                        Income_Sheet.season.desc()).first()
        elif mode == 'single':
            year = request.args.get('year')
            season = request.args.get('season')
            incomeSheet = db.session.query(Income_Sheet).filter_by(
                stock_id=stock_id).filter_by(
                    year=year).filter_by(
                        season=season).one_or_none()
        elif mode == 'multiple':
            year = request.args.get('year')
            season = 4 if year is None else int(year) * 4
            incomeSheet = db.session.query(Income_Sheet).filter_by(
                stock_id=stock_id).order_by(
                    Income_Sheet.year.desc()).order_by(
                        Income_Sheet.season.desc()).limit(season).all()
        else:
            incomeSheet = None

        if incomeSheet is None:
            res = make_response(json.dumps(
                'Failed to get %s Income Sheet.' % (stock_id)), 404)
            return res
        elif mode == 'single' or mode == None:
            res = [incomeSheet.serialize]
            return jsonify(res)
        else:
            res = [i.serialize for i in incomeSheet]
            return jsonify(res)

    def post(self, stock_id):
        """
        Create or Update stock_id's Income Sheet
        swagger_from_file: IncomeSheet_post.yml
        """
        payload = json.loads(request.data)
        incomeSheet = db.session.query(Income_Sheet).filter_by(
            stock_id=stock_id).filter_by(
                year=payload['year']).filter_by(
                    season=payload['season']).one_or_none()
        try:
            if incomeSheet is not None:
                changeFlag = False
                for key in payload:
                    if incomeSheet[key] != payload[key]:
                        changeFlag = True
                        incomeSheet[key] = payload[key]
                # If there is no data to modify, then return 200
                if changeFlag is not True:
                    return make_response(json.dumps('OK'), 200)
                # if there is any data to modify,
                # then record currennt date for update_date
                incomeSheet['update_date'] = datetime.datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                incomeSheet = Income_Sheet()
                incomeSheet['stock_id'] = stock_id
                for key in payload:
                    incomeSheet[key] = payload[key]

            db.session.add(incomeSheet)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Income Sheet. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Income Sheet.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print(ex)
            logger.warning(
                "400 %s is failed to update Income Sheet. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Income sheet.' % (stock_id)), 400)
            return res

        checkFourSeasonEPS(stock_id)
        res = make_response(
            json.dumps('Create'), 201)
        return res


class handleBalanceSheet(MethodView):
    """
    Description:
        this api is used to handle balance sheet request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's balance sheet.
        if request method is POST, then according to the data entered,
        decide whether to update or add new balance sheet data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's balance sheet.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        return 'balance_sheet: %s' % stock_id

    def post(self, stock_id):
        payload = json.loads(request.data)
        balanceSheet = db.session.query(Balance_Sheet).filter_by(
            stock_id=stock_id).filter_by(
                year=payload['year']).filter_by(
                    season=payload['season']).one_or_none()
        try:
            if balanceSheet is not None:
                changeFlag = False
                for key in payload:
                    if balanceSheet[key] != payload[key]:
                        changeFlag = True
                        balanceSheet[key] = payload[key]
                # If there is no data to modify, then return 200
                if changeFlag is not True:
                    return make_response(json.dumps('OK'), 200)
                # if there is any data to modify,
                # then record currennt date for update_date
                balanceSheet['update_date'] = datetime.datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                balanceSheet = Balance_Sheet()
                balanceSheet['stock_id'] = stock_id
                for key in payload:
                    balanceSheet[key] = payload[key]

            db.session.add(balanceSheet)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Balance Sheet. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Balance Sheet.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print(ex)
            logger.warning(
                "400 %s is failed to update Balance Sheett. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Balance Sheet.' % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res


class handleCashFlow(MethodView):
    """
    Description:
        this api is used to handle cash flow request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's cash flow.
        if request method is POST, then according to the data entered,
        decide whether to update or add new cash flow data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's cash flow.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        return 'cash_flow: %s' % stock_id

    def post(self, stock_id):
        payload = json.loads(request.data)
        cashFlow = db.session.query(Cash_Flow).filter_by(
            stock_id=stock_id).filter_by(
                year=payload['year']).filter_by(
                    season=payload['season']).one_or_none()
        try:
            if cashFlow is not None:
                changeFlag = False
                for key in payload:
                    if cashFlow[key] != payload[key]:
                        changeFlag = True
                        cashFlow[key] = payload[key]
                # If there is no data to modify, then return 200
                if changeFlag is not True:
                    return make_response(json.dumps('OK'), 200)
                # if there is any data to modify,
                # then record currennt date for update_date
                cashFlow['update_date'] = datetime.datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                cashFlow = Cash_Flow()
                cashFlow['stock_id'] = stock_id
                for key in payload:
                    cashFlow[key] = payload[key]

            db.session.add(cashFlow)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Cash Flowe. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Cash Flow.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print(ex)
            logger.warning(
                "400 %s is failed to update Cash Flow. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Cash Flow.' % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res


class handleMonthRevenue(MethodView):
    """
    Description:
        this api is used to handle month revenue request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's month reveune.
        if request method is POST, then according to the data entered,
        decide whether to update or add new data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's month revenue.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        """
        return stock's monthly revenue data for the last five years
        swagger_from_file: MonthRevenue_get.yml
        """
        monthReve = db.session.query(Month_Revenue).filter_by(
            stock_id=stock_id
        ).order_by(Month_Revenue.year.desc()).limit(60).all()
        if monthReve is None:
            return make_response(404)
        else:
            result = [i.serialize for i in monthReve]
            return jsonify(result)

    def post(self, stock_id):
        """
        Create or Update stock_id's month revenue data
        swagger_from_file: MonthRevenue_post.yml
        """
        payload = json.loads(request.data)
        monthReve = db.session.query(Month_Revenue).filter_by(
            stock_id=stock_id).filter_by(
                year=payload['year']).filter_by(
                    month=payload['month']).one_or_none()
        # check payload
        for key in payload:
            if payload[key] == '不適用':
                payload[key] = None

        try:
            if monthReve is not None:
                changeFlag = False
                for key in payload:
                    if monthReve[key] != payload[key]:
                        changeFlag = True
                        monthReve[key] = payload[key]
                # If there is no data to modify, then return 200
                if changeFlag is not True:
                    return make_response(json.dumps('OK'), 200)
                # if there is any data to modify,
                # then record currennt date for update_date
                monthReve['update_date'] = datetime.datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                monthReve = Month_Revenue()
                for key in payload:
                    monthReve[key] = payload[key]

            db.session.add(monthReve)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Month Revenue. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Month Revenue.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print("%s: %s" % (stock_id, ex))
            logging.warning(
                "400 %s is failed to update Month Revenue. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Month Revenue.' % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
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


def checkFourSeasonEPS(stock_id):
    quantityOfIncomeSheet = db.session.query(
        db.func.count(Income_Sheet.id)).filter_by(
            stock_id=stock_id).scalar()

    stockType = db.session.query(
        Basic_Information.exchangeType).filter_by(
            id=stock_id).scalar()

    if stockType in ('sii', 'otc') and quantityOfIncomeSheet >= 4:
        stockEps = db.session.query(
            (Income_Sheet.基本每股盈餘).label('eps')).filter_by(
                stock_id=stock_id).order_by(
                    Income_Sheet.year.desc()).order_by(
                        Income_Sheet.season.desc()).limit(4).subquery()
        fourSeasonEps = db.session.query(db.func.sum(stockEps.c.eps)).scalar()

        dailyInfo = db.session.query(
            Daily_Information).filter_by(
                stock_id=stock_id).one_or_none()
        try:
            if dailyInfo is not None:
                dailyInfo['近四季每股盈餘'] = round(fourSeasonEps, 2)
            else:
                dailyInfo = Daily_Information()
                dailyInfo['stock_id'] = stock_id
                dailyInfo['近四季每股盈餘'] = round(fourSeasonEps, 2)

            dailyInfo.updatePE()

            db.session.add(dailyInfo)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            print(ex)


main.add_url_rule('/',
                  'showMain',
                  view_func=showMain)
main.add_url_rule('/stock_number',
                  'getStockNumber',
                  view_func=getStockNumber.as_view(
                      'getStockNumber_api'),
                  methods=['GET', 'POST'])
main.add_url_rule('/basic_information/<stock_id>',
                  'handleBasicInfo',
                  view_func=handleBasicInfo.as_view(
                      'handleBasicInfo_api'),
                  methods=['GET', 'POST', 'PATCH'])
main.add_url_rule('/income_sheet/<stock_id>',
                  'handleIncomeSheet',
                  view_func=handleIncomeSheet.as_view(
                      'handleIncomeSheet'),
                  methods=['GET', 'POST'])
main.add_url_rule('/balance_sheet/<stock_id>',
                  'handleBalanceSheet',
                  view_func=handleBalanceSheet.as_view(
                      'handleBalanceSheet'),
                  methods=['GET', 'POST'])
main.add_url_rule('/cash_flow/<stock_id>',
                  'handleCashFlow',
                  view_func=handleCashFlow.as_view(
                      'handleCashFlow'),
                  methods=['GET', 'POST'])
main.add_url_rule('/month_revenue/<stock_id>',
                  'handleMonthRevenue',
                  view_func=handleMonthRevenue.as_view(
                      'handleMonthRevenue'),
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
