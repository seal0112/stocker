import logging
import json
from datetime import datetime

from flask import request, jsonify, make_response
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from app import db
from app.main import main
from app.utils.stock_screener import StockScreenerManager
from app.utils.discord_bot import DiscordBot
from app.utils.announcement_handler import AnnounceHandler
from app.database_setup import (
    BasicInformation, IncomeSheet, BalanceSheet,
    CashFlow, DailyInformation, StockCommodity
)
from app.models import Feed
from app.monthly_valuation.models import MonthlyValuation
from app.schemas.feed_schema import FeedSchema
from app.tasks.test_task.tasks import add
from app.tasks.feed_task.tasks import analyze_announcement_incomesheet


logger = logging.getLogger(__name__)
BASIC_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
DATE_FORMAT = '%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


def showMain():
    return 'Hello'


@main.route('screener')
def use_screener():
    option = request.args.get('option')
    stock_screener = StockScreenerManager(option)
    result = stock_screener.run_and_save()
    messages = result['messages']
    discord_bot = DiscordBot()
    for message in messages:
        discord_bot.push_message(option, message)

    return make_response('', 204)


@main.route('incomesheet_announce', methods=['POST'])
def get_incomesheet_announcement():
    payload = json.loads(request.data)

    announce_handler = AnnounceHandler(payload['link'])
    income_sheet = announce_handler.get_incomesheet_announce()
    single_season_incomesheet = announce_handler.get_single_season_incomesheet(
        income_sheet, payload['year'], payload['season'])
    return make_response(single_season_incomesheet)


def store_incomesheet_announcement():
    payload = json.loads(request.data)
    feed = Feed.query.filter_by(id=payload['feed_id']).one_or_none()
    if feed is None:
        res = make_response(json.dumps(
            'Failed to get %s Daily information.' % (payload['feed_id'])), 404)
        return res


    income_sheet = payload['income_sheet']
    announce_handler = AnnounceHandler(payload['link'])
    single_season_incomesheet = announce_handler.get_single_season_incomesheet(
        income_sheet, payload['year'], payload['season'])
    print(single_season_incomesheet)
    # announcement_income_sheet_analysis = AnnouncementIncomeSheetAnalysis(
    #     stock_id=payload['stock_id'],
    #     year=payload['year'],
    #     season=payload['season'],
    #     analysis=single_season_incomesheet
    # )
    # db.session.add(announcement_income_sheet_analysis)
    # db.session.commit()

    return make_response('', 204)

class getStockNumber(MethodView):
    decorators = []

    def get(self):
        query = db.session.query(BasicInformation.id)

        exchange_type = request.args.getlist('exchange_type')
        stock_number_start_with = request.args.get('stock_number_start_with')
        query = query.filter(BasicInformation.exchange_type.in_(exchange_type if exchange_type else ['sii', 'otc', 'rotc']))
        if stock_number_start_with:
            query = query.filter(BasicInformation.id.like(stock_number_start_with + '%'))

        stockNum = query.all()
        res = [i[0] for i in stockNum]

        return jsonify(res)

    def post(self):
        payload = json.loads(request.data)
        reportTypeSet = set(["balance_sheet", "income_sheet", "cashflow", "monthly_valuation"])
        try:
            if payload['reportType'] not in reportTypeSet:
                raise KeyError
            reportType = payload['reportType']
            if reportType == 'balance_sheet':
                stockNums = db.session.query(BalanceSheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'income_sheet':
                stockNums = db.session.query(IncomeSheet.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'cashflow':
                stockNums = db.session.query(CashFlow.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        season=payload['season']).all()
            elif reportType == 'monthly_valuation':
                stockNums = db.session.query(MonthlyValuation.stock_id).filter_by(
                    year=payload['year']).filter_by(
                        month=payload['month']).all()
            res = [i[0] for i in stockNums]
        except Exception as ex:
            if ex == KeyError:
                logger.warning(
                    "400 report type %s not found." % (reportType))
                res = make_response(
                    json.dumps('Failed to fetch stock number'), 400)
            else:
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
        dailyInfo = db.session.query(DailyInformation).filter_by(
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
        dailyInfo = db.session.query(DailyInformation).filter_by(
            stock_id=stock_id).one_or_none()
        try:
            if dailyInfo is not None:
                for key in payload:
                    dailyInfo[key] = payload[key]
                    dailyInfo['update_date'] = datetime.now(
                        ).strftime("%Y-%m-%d")
            else:
                dailyInfo = DailyInformation()
                dailyInfo['stock_id'] = stock_id
                for key in payload:
                    dailyInfo[key] = payload[key]

            db.session.add(dailyInfo)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            logging.warning(
                "400 %s is failed to update Daily price. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Daily price.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
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
        stockCommodity = db.session.query(StockCommodity).filter_by(
            stock_id=stock_id).one_or_none()
        return 'Stock Commodity: %s' % stock_id\
            if stockCommodity is None else stockCommodity.serialize

    def post(self, stock_id):
        payload = json.loads(request.data)
        stockCommodity = db.session.query(StockCommodity).filter_by(
            stock_id=stock_id).one_or_none()
        try:
            if stockCommodity is not None:
                for key in payload:
                    stockCommodity[key] = payload[key]
            else:
                stockCommodity = StockCommodity()
                stockCommodity['stock_id'] = stock_id
                for key in payload:
                    stockCommodity[key] = payload[key]

            db.session.add(stockCommodity)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            logging.warning(
                "400 %s is failed to update Stock Commodity. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Stock Commodity.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
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
main.add_url_rule('/StockCommodity/<stock_id>',
                  'handleStockCommodity',
                  view_func=handleStockCommodity.as_view(
                      'handleStockCommodity'),
                  methods=['GET', 'POST'])
