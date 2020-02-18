from flask import Flask, request, redirect, url_for
from flask import jsonify, make_response, render_template
from flask import Blueprint
from flask.views import MethodView
from sqlalchemy import asc, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database_setup import Base
from database_setup import (
    Basic_Information, Month_Revenue, Income_Sheet,
    Balance_Sheet, Cash_Flow, Daily_Information
)
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import datetime


# Read file databaseAccount.json in directory critical_flie
# then can get database username and password.
with open('./critical_flie/databaseAccount.json') as accountReader:
    dbAccount = json.loads(accountReader.read())

engine = create_engine(
    """mysql+pymysql://%s:%s@%s/stocker?charset=utf8""" % (
        dbAccount["username"], dbAccount["password"], dbAccount["ip"]))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

logger = logging.getLogger()
BASIC_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
DATE_FORMAT = '%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


def showMain():
    checkFourSeasonEPS(2330)
    b = session.query(Daily_Information).filter_by(
        stock_id='1785').all()
    res = [i.serialize for i in b]
    return jsonify(res)


class getStockNumber(MethodView):
    def get(self):
        companyType = request.args.get('type')
        if companyType is None:
            stockNum = session.query(Basic_Information.id).all()
        else:
            stockNum = session.query(
                Basic_Information.id).filter_by(type=companyType).all()
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
                stockNums = session.query(Balance_Sheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'income_sheet':
                stockNums = session.query(Income_Sheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'cashflow':
                stockNums = session.query(Cash_Flow.stock_id).filter_by(
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
        stock_id: a string of stock number.
    Return:
        if request method is GET,
            then return stock_id's basic information.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """
    def get(self, stock_id):
        basicInfo = session.query(Basic_Information).filter_by(
            id=stock_id).one_or_none()
        if basicInfo is None:
            return make_response(
                json.dumps("404 Not Found"), 404)
        else:
            return jsonify(basicInfo.serialize)

    def post(self, stock_id):
        basicInfo = session.query(Basic_Information).filter_by(
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

            session.add(basicInfo)
            session.commit()
        except IntegrityError as ie:
            session.rollback()
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
                    'Failed to update basic_information.'), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res


class handleDailyInfo(MethodView):
    def get(self, stock_id):
        dailyInfo = session.query(Daily_Information).filter_by(
            stock_id=stock_id).one_or_none()
        return 'Daily Information: %s' % stock_id\
            if dailyInfo is None else dailyInfo.serialize

    def post(self, stock_id):
        payload = json.loads(request.data)
        dailyInfo = session.query(Daily_Information).filter_by(
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

            session.add(dailyInfo)
            session.commit()
        except IntegrityError as ie:
            session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Daily Price. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Daily Price.' % (stock_id)), 400)
            return res
        except Exception as ex:
            session.rollback()
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
        stock_id: a string of stock number.
    Return:
        if request method is GET,
            then return stock_id's income sheet.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """
    def get(self, stock_id):
        mode = request.args.get('mode')
        if mode is None:
            incomeSheet = session.query(Income_Sheet).filter_by(
                stock_id=stock_id).order_by(
                    Income_Sheet.year.desc()).order_by(
                        Income_Sheet.season.desc()).first()
        elif mode == 'single':
            year = request.args.get('year')
            season = request.args.get('season')
            incomeSheet = session.query(Income_Sheet).filter_by(
                stock_id=stock_id).filter_by(
                    year=year).filter_by(
                        season=season).one_or_none()
        elif mode == 'multiple':
            year = request.args.get('year')
            season = 4 if year is None else int(year) * 4
            incomeSheet = session.query(Income_Sheet).filter_by(
                stock_id=stock_id).order_by(
                    Income_Sheet.year.desc()).order_by(
                        Income_Sheet.season.desc()).limit(season).all()
        else:
            incomeSheet = None

        if incomeSheet is None:
            res = make_response(json.dumps(
                    'Failed to get %s Income Sheet.' % (stock_id)), 404)
            return res
        elif type == 'single':
            res = [incomeSheet.serialize]
            return jsonify(res)
        else:
            res = [i.serialize for i in incomeSheet]
            return jsonify(res)

    def post(self, stock_id):
        payload = json.loads(request.data)
        incomeSheet = session.query(Income_Sheet).filter_by(
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

            session.add(incomeSheet)
            session.commit()
        except IntegrityError as ie:
            session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Income Sheet. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Income Sheet.' % (stock_id)), 400)
            return res
        except Exception as ex:
            session.rollback()
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
        stock_id: a string of stock number.
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
        balanceSheet = session.query(Balance_Sheet).filter_by(
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

            session.add(balanceSheet)
            session.commit()
        except IntegrityError as ie:
            session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Balance Sheet. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Balance Sheet.' % (stock_id)), 400)
            return res
        except Exception as ex:
            session.rollback()
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
        stock_id: a string of stock number.
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
        cashFlow = session.query(Cash_Flow).filter_by(
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

            session.add(cashFlow)
            session.commit()
        except IntegrityError as ie:
            session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Cash Flowe. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Cash Flow.' % (stock_id)), 400)
            return res
        except Exception as ex:
            session.rollback()
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
        stock_id: a string of stock number.
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
        monthReve = session.query(Month_Revenue).filter_by(
            stock_id=stock_id
            ).order_by(Month_Revenue.year.desc()).limit(60).all()
        print(monthReve)
        if monthReve is None:
            return make_response(404)
        else:
            result = [i.serialize for i in monthReve]
            return jsonify(result)

    def post(self, stock_id):
        payload = json.loads(request.data)
        monthReve = session.query(Month_Revenue).filter_by(
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

            session.add(monthReve)
            session.commit()
        except IntegrityError as ie:
            session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Month Revenue. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Month Revenue.' % (stock_id)), 400)
            return res
        except Exception as ex:
            session.rollback()
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


def checkFourSeasonEPS(stock_id):
    quantityOfIncomeSheet = session.query(
        func.count(Income_Sheet.id)).filter_by(
            stock_id=stock_id).scalar()

    stockType = session.query(
        Basic_Information.type).filter_by(
            id=stock_id).scalar()

    if stockType in ('sii', 'otc') and quantityOfIncomeSheet >= 4:
        stockEps = session.query(
            (Income_Sheet.基本每股盈餘).label('eps')).filter_by(
                stock_id=stock_id).order_by(
                    Income_Sheet.year.desc()).order_by(
                        Income_Sheet.season.desc()).limit(4).subquery()
        fourSeasonEps = session.query(func.sum(stockEps.c.eps)).scalar()

        dailyInfo = session.query(
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

            session.add(dailyInfo)
            session.commit()
        except Exception as ex:
            session.rollback()
            print(ex)
