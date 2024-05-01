from .. import ma


class EarningsCallchema(ma.Schema):
    class Meta:
        fields = (
            "stock_id", "meeting_date", "meeting_end_date",
            "location", "description", "file_name_chinese"
        )