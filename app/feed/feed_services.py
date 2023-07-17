import logging
import json

from flask import jsonify, make_response
from datetime import datetime

from ..database_setup import Feed, FeedTag
from ..basic_information.basic_information_services import BasicInformationServices
from ..utils.data_update_date_service import DataUpdateDateService
from .. import db


logger = logging.getLogger()
basic_info_services = BasicInformationServices()
data_update_date_service = DataUpdateDateService()


class FeedServices:
    def __init__(self):
        self.feed_size = 15

    def get_feeds(self, stock_id, time):
        stock = basic_info_services.get_basic_information(stock_id)
        feeds = stock.feeds.filter(
            Feed.releaseTime<time).order_by(
                Feed.releaseTime.desc()).limit(self.feed_size).all()
        res = [feed.serialize for feed in feeds]
        return res

    def get_feeds_by_time_range(self, start_time, end_time):
        feeds = Feed.query.filter(
            Feed.releaseTime.between(start_time, end_time)).order_by(
                Feed.releaseTime.desc()).all()
        res = [feed.serialize for feed in feeds]
        return res

    def create_feed(self, feed_data):
        releaseTime = datetime.fromisoformat(feed_data['releaseTime'])
        feed = Feed.query.filter_by(
            link=feed_data['link']
        ).one_or_none()

        if feed == None:
            feed = Feed()

        try:
            feed.releaseTime = releaseTime
            feed.title = feed_data['title']
            feed.link = feed_data['link']
            feed.source = feed_data['source']
            feed.description = feed_data.get('description', None)
            feed.feedType = feed_data['feedType']
            for tag_name in feed_data['tags']:
                tag = self.get_feed_tag(tag_name)
                feed.tags.append(tag)

            for stock_id in feed_data['stocks']:
                stock = basic_info_services.get_basic_information(stock_id)
                if stock:
                    data_update_date_service.update_feed_update_date(stock_id)
                    feed.stocks.append(stock)

            db.session.add(feed)
            db.session.commit()
        except Exception as ex:
            logging.exception(ex)
            db.session.rollback()
            return make_response(json.dumps(str(ex)), 500)
        else:
            return make_response(json.dumps('Create'), 201)

    def get_feed_tag(self, tag_name):
        tag = FeedTag.query.filter_by(name=tag_name).one_or_none()
        if tag == None:
            return FeedTag(name=tag_name)
        else:
            return tag
