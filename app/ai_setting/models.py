from datetime import datetime
from app import db


class AiSetting(db.Model):
    __tablename__ = 'ai_setting'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider = db.Column(db.String(50), nullable=False, default='gemini')
    updated_by = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
