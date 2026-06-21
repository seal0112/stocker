from .. import ma
from .models import AiReport


class AiReportSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AiReport
        fields = (
            "id", "report_type", "subject", "period_start", "period_end",
            "prompt_name", "ref_id",
            "processing_status", "error_message",
            "summary", "key_points",
            "score", "sentiment",
            "input_tokens", "output_tokens", "total_tokens",
            "cost_usd", "cost_twd", "model_name",
            "created_at", "updated_at",
        )
        load_instance = False
        include_fk = True
