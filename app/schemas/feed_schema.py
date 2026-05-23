
from app import ma
from app.models import Feed


class FeedSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feed
        fields = (
            "id", "stock_id", "update_date", "releaseTime",
            "title", "link", "description", "feedType", "source"
        )
        include_fk = True
        load_instance = False
