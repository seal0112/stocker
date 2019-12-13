from flask import Flask, request, redirect, url_for
from flask import jsonify, make_response, render_template
from flask import Blueprint
from flask.views import MethodView
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base
from database_setup import Basic_information, Month_revenue, Income_sheet
from database_setup import Balance_Sheet
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
    b = session.query(Basic_information).filter_by(
        id='1101').one_or_none()
    res = b.serialize
    return jsonify(res)


class getStockNumber(MethodView):
    def get(self):
        companyType = request.args.get('type')
        if companyType is None:
            stockNum = session.query(Basic_information.id).all()
        else:
            stockNum = session.query(
                Basic_information.id).filter_by(type=companyType).all()
        res = [i[0] for i in stockNum]

        return jsonify(res)

    def post(self):
        payload = json.loads(request.data)
        reportTypeSet = set(["balance_sheet", "income_sheet"])
        try:
            if payload['reportType'] not in reportTypeSet:
                raise KeyError
            reportType = payload['reportType']
            if reportType == 'balance_sheet':
                stockNums = session.query(Balance_Sheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'income_sheet':
                stockNums = session.query(Income_sheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            res = [i[0] for i in stockNums]
        except Exception as ex:
            if ex == KeyError:
                logger.warning(
                    "406 report type %s not found." % (reportType))
                res = make_response(
                    json.dumps('Failed to fetch stock number'), 406)
            else:
                print(ex)
                logger.warning(
                    "406 stock id not found. Reason: %s" % (ex))
                res = make_response(
                    json.dumps(
                        'Failed to update basic_information.'), 406)
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
        basicInfo = session.query(Basic_information).filter_by(
            id=stock_id).one_or_none()
        if basicInfo is None:
            return make_response(
                json.dumps("404 Not Found"), 404)
        else:
            return jsonify(basicInfo.serialize)

    def post(self, stock_id):
        basicInfo = session.query(Basic_information).filter_by(
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
                basicInfo = Basic_information()
                for key in payload:
                    basicInfo[key] = payload[key]

            session.add(basicInfo)
            session.commit()
        except Exception as ex:
            print(ex)
            logger.warning(
                "406 %s is failed to update basic_information. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update basic_information.'), 406)
            return res

        res = make_response(
            json.dumps('Create'), 201)
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
        return 'income_sheet: %s' % stock_id

    def post(self, stock_id):
        payload = json.loads(request.data)
        incomeSheet = session.query(Income_sheet).filter_by(
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
                incomeSheet = Income_sheet()
                incomeSheet['stock_id'] = stock_id
                for key in payload:
                    incomeSheet[key] = payload[key]

            session.add(incomeSheet)
            session.commit()
        except Exception as ex:
            print(ex)
            logger.warning(
                "406 %s is failed to update income_sheet. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s balance sheet.' % (stock_id)), 406)
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
        monthReve = session.query(Month_revenue).filter_by(
            stock_id=stock_id).order_by(Month_revenue.year.desc()).all()
        print(monthReve)
        if monthReve is None:
            return make_response(404)
        else:
            result = [i.serialize for i in monthReve]
            return jsonify(result)

    def post(self, stock_id):
        payload = json.loads(request.data)
        monthReve = session.query(Month_revenue).filter_by(
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
                monthReve = Month_revenue()
                for key in payload:
                    monthReve[key] = payload[key]

            session.add(monthReve)
            session.commit()
        except Exception as ex:
            print("%s: %s" % (stock_id, ex))
            logging.warning(
                "406 %s is failed to update month revenue. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s month revenue.' % (stock_id)), 406)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res
