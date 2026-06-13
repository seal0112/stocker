from datetime import datetime

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


class EarningsCallSummary(db.Model):
    """AI-generated summary of earnings call based on related news feeds."""
    __tablename__ = 'earnings_call_summary'

    id = db.Column(db.Integer, primary_key=True)
    earnings_call_id = db.Column(
        db.Integer, db.ForeignKey('earnings_call.id'), nullable=False, unique=True)
    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'), nullable=False)

    # AI 摘要欄位（質化分析）
    capex = db.Column(db.Text)
    capex_industry = db.Column(db.Text)
    outlook = db.Column(db.Text)
    concerns_and_risks = db.Column(db.Text)

    # 評分系統
    score = db.Column(db.Integer)                   # -5 to +5
    sentiment = db.Column(db.String(20))            # Strong Buy/Buy/Neutral/Sell/Strong Sell
    impact_duration = db.Column(db.String(20))      # Short/Medium/Long
    source_reliability = db.Column(db.String(20))   # Official/Analyst/Media
    reasoning = db.Column(db.Text)
    news_contributions = db.Column(db.JSON)         # 每篇新聞的分數貢獻

    # 元資料
    source_feed_ids = db.Column(db.JSON)  # 來源新聞 IDs
    raw_ai_response = db.Column(db.Text)  # 原始 AI 回應 (debug)
    processing_status = db.Column(
        db.Enum('pending', 'processing', 'completed', 'failed', name='processing_status_enum'),
        nullable=False, default='pending')
    error_message = db.Column(db.Text)  # 錯誤訊息
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Token 使用量與費用
    input_tokens = db.Column(db.Integer)  # 輸入 tokens
    output_tokens = db.Column(db.Integer)  # 輸出 tokens
    total_tokens = db.Column(db.Integer)  # 總 tokens
    cost_usd = db.Column(db.Numeric(10, 6))  # 費用 (USD)
    cost_twd = db.Column(db.Numeric(10, 2))  # 費用 (TWD)
    model_name = db.Column(db.String(100))  # 使用的 AI 模型名稱

    # Relationships
    earnings_call = db.relationship("EarningsCall", backref=db.backref("summary", uselist=False))
    stock = db.relationship("BasicInformation", lazy="immediate")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
