import logging

from app import db
from app.utils.model_utilities import get_current_date

from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis


class Feed(db.Model):
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(6), db.ForeignKey('basic_information.id'), nullable=True)
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
        'FeedTag',
        secondary='feed_feedTag',
        backref=db.backref('feeds', lazy='dynamic'),
        lazy='joined'
    )
    announcement_income_sheet_analysis = db.relationship(
        'AnnouncementIncomeSheetAnalysis',
        uselist=False,
        backref='feed'
    )
    stock = db.relationship('BasicInformation', backref='feeds', lazy='joined')

    @property
    def serialize(self):
        res = {}
        tags = []
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            else:
                res[attr] = val
        if self.tags:
            tags = [tag.name for tag in self.tags]
        res['tags'] = tags
        return res

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


    def create_default_announcement_income_sheet_analysis(self):
        if self.announcement_income_sheet_analysis is None:
            self.announcement_income_sheet_analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=self.id,
                stock_id=self.stock_id,
            )
            try:
                db.session.add(self.announcement_income_sheet_analysis)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logging.exception(e)

        return self.announcement_income_sheet_analysis

    def create_announcement_income_sheet_analysis(self, announcement_income_sheet_analysis: dict):
        announcement_income_sheet = self.create_default_announcement_income_sheet_analysis()

        for key, value in announcement_income_sheet_analysis.items():
            if hasattr(announcement_income_sheet, key):
                setattr(announcement_income_sheet, key, value)

        try:
            db.session.add(announcement_income_sheet)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
