import json
import logging
import re
from datetime import datetime, timedelta

from flask import request, jsonify, make_response
from flask.views import MethodView


from .. import db
from . import feed

from app.feed.feed_services import FeedServices
from app.feed.models import AnnouncementIncomeSheetAnalysis
from app.feed.serializer import AnnouncementIncomeSheetAnalysisSchema

from app.utils.model_utilities import get_current_date
from app.utils.aws_service import AWSService
from app.utils.announcement_handler import AnnounceHandler


logger = logging.getLogger()
feed_services = FeedServices()


@feed.route('/<stock_id>', methods=['GET'])
def get_stock_feed(stock_id):
    time = request.args.get('time', default=None)
    time = time if time else datetime.now()
    feeds = feed_services.get_feeds(stock_id, time)
    return jsonify(feeds)


class handleFeed(MethodView):
    """
    Description:
        this api is used to handle Stock Feed request.
    Detail:
        According to the received stock_id and request method(GET/POST),
        if request method is GET, then return stock_id's Feed.
        if request method is POST, then according to the data entered,
        decide whether to update or add new Feed into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's Feed.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred then return 400.
    """

    def get(self):
        start_time = request.args.get(
            'starttime', default=None)
        end_time = request.args.get(
            'endtime', default=None)
        start_time = datetime.strptime(
            start_time, '%Y-%m-%d') if start_time else datetime.now().replace(
                hour=0, minute=0, microsecond=0) - timedelta(days=1)
        end_time = datetime.strptime(
            end_time, '%Y-%m-%d') if end_time else datetime.now()
        feeds = feed_services.get_feeds_by_time_range(start_time, end_time)
        return jsonify(feeds)

    def post(self):
        try:
            feed_data = json.loads(request.data)
            feed = feed_services.create_feed(feed_data)

            if re.search(r'財報|財務報', feed.title) and (not '日期' in feed.title):
                announcement_income_sheet_analysis = feed.create_default_announcement_income_sheet_analysis()
                announcement_income_sheet_analysis.analysis_announcement_income_sheet()

            return make_response('Created', 201)
        except Exception as ex:
            logging.exception(ex)
            db.session.rollback()
            return make_response(json.dumps(str(ex)), 500)


feed.add_url_rule('',
                  view_func=handleFeed.as_view(
                      'handleFeed'),
                  methods=['GET', 'POST'])


class AnnouncementIncomeSheetAnalysisListApi(MethodView):
    def get(self):
        return 'announcement_income_sheet_analysis'


class AnnouncementIncomeSheetAnalysisDetailApi(MethodView):
    def put(self, feed_id):
        anouncement_income_sheet_data = json.loads(request.data)
        print(f'request.data: {anouncement_income_sheet_data}')
        feed = feed_services.get_feed(feed_id)
        income_sheet = anouncement_income_sheet_data['income_sheet']
        year = anouncement_income_sheet_data['year']
        season = anouncement_income_sheet_data['season']

        try:
            announce_handler = AnnounceHandler()
            single_season_incomesheet = announce_handler.calculate_income_sheet_annual_growth_rate(
                income_sheet, year, season
            )
        except Exception as e:
            single_season_incomesheet = {}
            single_season_incomesheet['processing_failed'] = True
        finally:
            single_season_incomesheet['feed_id'] = feed_id
            single_season_incomesheet['year'] = year
            single_season_incomesheet['season'] = str(season)
            single_season_incomesheet['update_date'] = get_current_date()

        announcement_income_sheet_analysis = feed.create_default_announcement_income_sheet_analysis()
        for key in single_season_incomesheet:
            announcement_income_sheet_analysis[key] = single_season_incomesheet[key]

        try:
            db.session.add(announcement_income_sheet_analysis)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(e)

        return AnnouncementIncomeSheetAnalysisSchema().dumps(announcement_income_sheet_analysis), 200


# def analyze_announcement_incomesheet(feed_id, link, year=2024, season=1):
#     announce_handler = AnnounceHandler(link)
#     try:
#         income_sheet = announce_handler.get_incomesheet_announce()
#         print(income_sheet)
#         single_season_incomesheet = announce_handler.get_single_season_incomesheet(
#             income_sheet, year, season)
#         single_season_incomesheet = announce_handler.calculate_income_sheet_annual_growth_rate(
#             single_season_incomesheet, year, season)
#     except Exception as e:
#         single_season_incomesheet = {}
#         single_season_incomesheet['processing_failed'] = True
#     finally:
#         single_season_incomesheet['feed_id'] = feed_id
#         single_season_incomesheet['year'] = year
#         single_season_incomesheet['season'] = str(season)
#         single_season_incomesheet['update_date'] = get_current_date()

#     announcement_income_sheet = AnnouncementIncomeSheetAnalysis.query.filter_by(feed_id=feed_id).one_or_none()
#     if announcement_income_sheet:
#         for key in single_season_incomesheet:
#             announcement_income_sheet[key] = single_season_incomesheet[key]
#     else:
#         announcement_income_sheet = AnnouncementIncomeSheetAnalysis(**single_season_incomesheet)

#     try:
#         db.session.add(announcement_income_sheet)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         logger.error(e)

#     return single_season_incomesheet


feed.add_url_rule('/announcement_income_sheet_analysis',
                  view_func=AnnouncementIncomeSheetAnalysisListApi.as_view(
                      'handleAnnouncementIncomeSheetAnalysis'),
                  methods=['GET'])

feed.add_url_rule('/<feed_id>/announcement_income_sheet_analysis',
                  view_func=AnnouncementIncomeSheetAnalysisDetailApi.as_view(
                      'handleAnnouncementIncomeSheetAnalysisDetail'),
                  methods=['PUT'])
