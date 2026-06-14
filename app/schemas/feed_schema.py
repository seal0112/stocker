
from marshmallow import fields

from app import ma
from app.models import Feed


class FeedSchema(ma.SQLAlchemyAutoSchema):
    company_name = fields.Method('get_company_name')

    def get_company_name(self, obj):
        return obj.stock.公司名稱 if obj.stock else None

    class Meta:
        model = Feed
        fields = (
            "id", "stock_id", "company_name", "update_date", "releaseTime",
            "title", "link", "description", "feedType", "source"
        )
        include_fk = True
        load_instance = False
