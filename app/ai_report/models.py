from datetime import datetime

from .. import db


class AiReport(db.Model):
    __tablename__ = 'ai_report'

    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(
        db.Enum('earnings_call', 'news', name='ai_report_type_enum'),
        nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False, index=True)
    period_start = db.Column(db.Date, nullable=False, index=True)
    period_end = db.Column(db.Date, nullable=False)
    prompt_name = db.Column(db.String(100), nullable=False)
    ref_id = db.Column(db.Integer, nullable=True)   # earnings_call_id for earnings_call type

    processing_status = db.Column(
        db.Enum('pending', 'processing', 'completed', 'failed', name='ai_report_status_enum'),
        nullable=False, default='pending')
    error_message = db.Column(db.Text)

    summary = db.Column(db.Text)
    key_points = db.Column(db.JSON)

    # Promoted fields for common queries / list display
    score = db.Column(db.Integer)       # -5 to +5 (earnings_call type)
    sentiment = db.Column(db.String(20))  # Strong Buy/Buy/Neutral/Sell/Strong Sell

    raw_ai_response = db.Column(db.Text)
    input_tokens = db.Column(db.Integer)
    output_tokens = db.Column(db.Integer)
    total_tokens = db.Column(db.Integer)
    cost_usd = db.Column(db.Numeric(10, 6))
    cost_twd = db.Column(db.Numeric(10, 2))
    model_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            'report_type', 'subject', 'period_start', 'period_end',
            name='uix_ai_report_type_subject_period'),
    )

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
