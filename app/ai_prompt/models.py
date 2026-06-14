from datetime import datetime

from .. import db


class AiPrompt(db.Model):
    __tablename__ = 'ai_prompt'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=True, index=True)  # gemini / claude / None（通用）
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.String(200))
    api_key_id = db.Column(db.Integer, db.ForeignKey('ai_api_key.id'), nullable=True)
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    api_key = db.relationship('AiApiKey', lazy='joined')

    __table_args__ = (
        db.UniqueConstraint('name', 'provider', name='uix_ai_prompt_name_provider'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'content': self.content,
            'is_active': self.is_active,
            'description': self.description,
            'api_key_id': self.api_key_id,
            'api_key_ssm_path': self.api_key.ssm_path if self.api_key else None,
            'api_key_name': self.api_key.name if self.api_key else None,
            'api_key_model': self.api_key.model if self.api_key else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
