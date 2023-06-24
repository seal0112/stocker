import logging
import json
from datetime import datetime

from flask import request, jsonify, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from ..utils.data_update_date_service import DataUpdateDateService
from ..database_setup import (
    Basic_Information, Income_Sheet, Daily_Information
)
from .. import db
from . import income_sheet


logger = logging.getLogger()
data_update_date_service = DataUpdateDateService()


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
                incomeSheet['update_date'] = datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                data_update_date_service.update_income_sheet_update_date(stock_id)
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

            db.session.add(dailyInfo)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logging.exception(ex)


income_sheet.add_url_rule('/<stock_id>',
                  view_func=handleIncomeSheet.as_view(
                      'handleIncomeSheet'),
                  methods=['GET', 'POST'])
