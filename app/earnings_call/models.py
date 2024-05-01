from .. import db


class EarningsCall(db.Model):
    __tablename__ = 'earnings_call'

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False, index=True)
    meeting_end_date = db.Column(db.Date)
    location = db.Column(db.String(100))
    description = db.Column(db.String(200))
    file_name_chinese = db.Column(db.String(100))

    stock = db.relationship("BasicInformation", lazy="immediate")

    @property
    def serialize(self):
        return {
            "id": self.id,
            "stock_id": self.stock_id,
            "date": self.meeting_date,
            "location": self.location,
            "description": self.description
        }

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
