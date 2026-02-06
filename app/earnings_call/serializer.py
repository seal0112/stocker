from .. import ma
from .models import EarningsCall, EarningsCallSummary


class EarningsCallchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EarningsCall
        fields = (
            "id", "stock_id", "meeting_date", "meeting_end_date",
            "location", "description", "file_name_chinese"
        )
        load_instance = False
        include_fk = True


class EarningsCallSummarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EarningsCallSummary
        fields = (
            "id", "earnings_call_id", "stock_id",
            "capex", "capex_industry",
            "outlook", "concerns_and_risks",
            "key_points", "source_feed_ids",
            "processing_status", "error_message",
            "input_tokens", "output_tokens", "total_tokens",
            "cost_usd", "cost_twd",
            "created_at", "updated_at"
        )
        load_instance = False
        include_fk = True