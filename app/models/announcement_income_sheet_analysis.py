import math
import json

from app import db
from app.utils.model_utilities import get_current_date
from app.utils.aws_service import AWSService


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
    year = db.Column(db.Integer)
    season = db.Column(db.Enum('1', '2', '3', '4'))
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

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def analysis_announcement_income_sheet(self):
        release_time = self.feed.releaseTime
        season = math.ceil((release_time.month + 1) / 3) - 1
        season = 4 if season == 0 else season
        feed_data = {
            'feed_id': self.feed_id,
            'link': self.feed.link,
            'year': release_time.year,
            'season': season,
            'stock_id': self.stock_id
        }
        aws_service = AWSService()
        aws_service.send_message_to_sqs(json.dumps(feed_data))

    def calculate_ratio(self):
        RATIO_KEYS = ['營業毛利', '營業利益', '稅前淨利', '本期淨利']

        for ratio_key in RATIO_KEYS:
            if self.營業收入合計 == 0:
                setattr(self, ratio_key + '率', None)
            else:
                setattr(self, ratio_key + '率', round(
                    getattr(self, ratio_key) / self.營業收入合計 * 100, 2))

        setattr(self, '本業佔比', 0 if self.稅前淨利率 == 0 else round(
            self.營業利益率 / self.稅前淨利率 * 100, 2)
        )
