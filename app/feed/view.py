from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import (
    Feed, FeedTag, basicInformationAndFeed
)
from .. import db
from . import feed
from .feed_services import FeedServices
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger()
feed_services = FeedServices()


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
        print(start_time, end_time)
        feeds = feed_services.get_feeds_by_time_range(start_time, end_time)
        return jsonify(feeds)

    def post(self):
        try:
            feed_data = json.loads(request.data)
            return feed_services.create_feed(feed_data)
        except Exception as ex:
            logging.exception(ex)
            db.session.rollback()
            return make_response(json.dumps(str(ex)), 500)
        else:
            return make_response(json.dumps('Create'), 201)


@feed.route('/<stock_id>', methods=['GET'])
def get_stock_feed(stock_id):
    time = request.args.get('time', default=None)
    time = time if time else datetime.now()
    feeds = feed_services.get_feeds(stock_id, time)
    return jsonify(feeds)


feed.add_url_rule('',
                  view_func=handleFeed.as_view(
                      'handleFeed'),
                  methods=['GET', 'POST'])
