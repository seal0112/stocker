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