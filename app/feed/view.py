from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import (
    Feed, FeedTag, basicInformationAndFeed
)
from .. import db
from . import feed
from .feed_services import FeedServices
import json
from datetime import datetime
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

    def get(self, stock_id):
        time = request.args.get(
            'time', default=None)
        time = time if time else datetime.now()
        feeds = feed_services.get_feeds(stock_id, time)
        return jsonify(feeds)


    def post(self, stock_id):
        feedData = json.loads(request.data)
        releaseTime = datetime.fromisoformat(feedData['releaseTime'])
        feed = Feed.query.filter_by(
            stock_id=stock_id,
            title=feedData['title'],
            releaseTime=releaseTime).one_or_none()

        if feed != None:
            return make_response(json.dumps('OK'), 200)

        try:
            feed = Feed()
            feed.stock_id = stock_id
            feed.releaseTime = releaseTime
            feed.title = feedData['title']
            feed.link = feedData['link']
            feed.description = feedData.get('description', None)
            feed.feedType = feedData['feedType']
            for tagName in feedData['tags']:
                tag = FeedTag.query.filter_by(
                    name=tagName).one_or_none()
                if tag == None:
                    feed.tags.append(FeedTag(name=tagName))
                else:
                    feed.tags.append(tag)

            db.session.add(feed)
            db.session.commit()
        except Exception as ex:
            logging.exception(ex)
            db.session.rollback()
            return make_response(json.dumps(str(ex)), 500)
        else:
            return make_response(json.dumps('Create'), 201)


@feed.route('', methods=['POST'])
def create_feed():
    feed_data = json.loads(request.data)
    return feed_services.create_feed(feed_data)


feed.add_url_rule('/<stock_id>',
                  view_func=handleFeed.as_view(
                      'handleFeed'),
                  methods=['GET', 'POST'])
