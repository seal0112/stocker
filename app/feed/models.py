from .. import db
from ..utils.model_utilities import get_current_date
from app.database_setup import basicInformationAndFeed


feedsAndfeedsTags = db.Table('feed_feedTag',
                             db.Column('feed_id', db.Integer, db.ForeignKey(
                                 'feed.id'), primary_key=True),
                             db.Column('feedTag', db.Integer, db.ForeignKey(
                                 'feed_tag.id'), primary_key=True)
                             )


class Feed(db.Model):
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True)
    update_date = db.Column(
        db.Date, nullable=False, default=get_current_date
    )
    releaseTime = db.Column(db.DateTime, nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(600), nullable=False, unique=True)
    source = db.Column(db.String(20), default='mops')
    description = db.Column(db.Text)
    feedType = db.Column(
        db.Enum('announcement', 'news'),
        nullable=False, default='announcement')
    tags = db.relationship(
        'FeedTag', secondary=feedsAndfeedsTags,
        backref=db.backref('feeds', lazy='dynamic'),
        lazy='joined'
    )
    stocks = db.relationship(
        'BasicInformation',
        secondary=basicInformationAndFeed,
        backref=db.backref('feeds', lazy='dynamic'),
        lazy='dynamic'
    )

    @property
    def serialize(self):
        res = {}
        tags = []
        stocks = []
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            else:
                res[attr] = val
        if self.tags:
            tags = [tag.name for tag in self.tags]
        res['tags'] = tags
        if self.stocks:
            stocks = [stock.id for stock in self.stocks]
        res['stocks'] = stocks
        return res

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class FeedTag(db.Model):
    __tablename__ = 'feed_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name
        }


class AnnouncementIncomeSheetAnalysis(db.Model):
    __tablename__ = 'announcement_income_sheet_analysis'

    feed_id = db.Column(
        db.Integer, db.ForeignKey('feed.id'),
        primary_key=True, nullable=False)
    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'))
    update_date = db.Column(
        db.Date, nullable=False,
        default=get_current_date,
        index=True
    )
    year = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Enum('1', '2', '3', '4'), nullable=False)
    processing_failed = db.Column(db.Boolean, nullable=False, default=False)
    營業收入合計 = db.Column(db.BigInteger)
    營業收入合計年增率 = db.Column(db.Numeric(10, 2))
    營業毛利 = db.Column(db.BigInteger)
    營業毛利率 = db.Column(db.Numeric(10, 2))
    營業毛利率年增率 = db.Column(db.Numeric(10, 2))
    營業利益 = db.Column(db.BigInteger)
    營業利益率 = db.Column(db.Numeric(10, 2))
    營業利益率年增率 = db.Column(db.Numeric(10, 2))
    稅前淨利 = db.Column(db.BigInteger)
    稅前淨利率 = db.Column(db.Numeric(10, 2))
    稅前淨利率年增率 = db.Column(db.Numeric(10, 2))
    本期淨利 = db.Column(db.BigInteger)
    本期淨利率 = db.Column(db.Numeric(10, 2))
    本期淨利率年增率 = db.Column(db.Numeric(10, 2))
    母公司業主淨利 = db.Column(db.BigInteger)
    基本每股盈餘 = db.Column(db.Numeric(10, 2))
    基本每股盈餘年增率 = db.Column(db.Numeric(10, 2))
    本業佔比 = db.Column(db.Numeric(5, 2))
    # feed = db.relationship('Feed', uselist=False)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
