from marshmallow import fields
from .. import ma
from .models import EarningsCall


class EarningsCallchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EarningsCall
        fields = (
            "id", "stock_id", "meeting_date", "meeting_end_date",
            "location", "description", "file_name_chinese"
        )
        load_instance = False
        include_fk = True


class EarningsCallSummarySchema(ma.Schema):
    """Serialize AiReport objects for earnings call summary endpoints."""

    id = fields.Int(dump_only=True)
    earnings_call_id = fields.Function(lambda obj: obj.ref_id)
    stock_id = fields.Function(lambda obj: obj.subject)
    processing_status = fields.Str()
    error_message = fields.Str(allow_none=True)

    capex = fields.Function(lambda obj: (obj.key_points or {}).get('capex'))
    capex_industry = fields.Function(lambda obj: (obj.key_points or {}).get('capex_industry'))
    outlook = fields.Function(lambda obj: (obj.key_points or {}).get('outlook'))
    concerns_and_risks = fields.Function(lambda obj: (obj.key_points or {}).get('concerns_and_risks'))
    reasoning = fields.Function(lambda obj: obj.summary)
    score = fields.Int(allow_none=True)
    sentiment = fields.Str(allow_none=True)
    impact_duration = fields.Function(lambda obj: (obj.key_points or {}).get('impact_duration'))
    source_reliability = fields.Function(lambda obj: (obj.key_points or {}).get('source_reliability'))
    news_contributions = fields.Function(lambda obj: (obj.key_points or {}).get('news_contributions'))
    source_feed_ids = fields.Function(lambda obj: (obj.key_points or {}).get('source_feed_ids'))

    model_name = fields.Str(allow_none=True)
    input_tokens = fields.Int(allow_none=True)
    output_tokens = fields.Int(allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)