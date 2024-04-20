from .. import ma


class EarningsCallchema(ma.Schema):
    class Meta:
        fields = (
            "stock_id", "meeting_date", "location", "description"
        )