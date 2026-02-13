from app.log_config import get_logger
from datetime import datetime

from app.models import Feed, FeedTag
from app.basic_information.basic_information_services import BasicInformationServices
from app.utils.data_update_date_service import DataUpdateDateService
from app import db


logger = get_logger(__name__)


class FeedServices():
    def __init__(self):
        self.feed_size = 15
        self.basic_info_services = BasicInformationServices()
        self.data_update_date_service = DataUpdateDateService()

    def get_feed(self, feed_id):
        return Feed.query.filter_by(id=feed_id).one_or_none()

    def get_feeds(self, stock_id, time):
        feeds = Feed.query.filter(
            Feed.stock_id == stock_id,
            Feed.releaseTime < time
        ).order_by(Feed.releaseTime.desc()).limit(self.feed_size).all()
        return feeds

    def get_feeds_by_time_range(self, start_time, end_time):
        feeds = Feed.query.filter(
            Feed.releaseTime.between(start_time, end_time)).order_by(
                Feed.releaseTime.desc()).all()
        return feeds

    def create_feed(self, feed_data):
        releaseTime = datetime.fromisoformat(feed_data['releaseTime'])
        feed = Feed.query.filter_by(
            link=feed_data['link']
        ).one_or_none()

        if feed is None:
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

            stocks = feed_data.get('stocks')
            if isinstance(stocks, list) and stocks:
                stock_id = stocks[0]
            else:
                stock_id = feed_data.get('stock_id', None)

            stock = self.basic_info_services.get_basic_information(stock_id)
            feed.stock = stock

            if stock:
                if feed_data['feedType'] == 'news':
                    self.data_update_date_service.update_news_update_date(stock_id)
                else:
                    if len(feed_data['tags']):
                        self.   data_update_date_service.update_announcement_update_date(stock_id)

            db.session.add(feed)
            db.session.commit()
        except Exception as ex:
            logger.exception(ex)
            db.session.rollback()
            return None
        else:
            return feed

    def get_feed_tag(self, tag_name):
        tag = FeedTag.query.filter_by(name=tag_name).one_or_none()
        if tag is None:
            return FeedTag(name=tag_name)
        else:
            return tag
