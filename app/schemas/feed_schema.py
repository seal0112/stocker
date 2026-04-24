
from app import ma
from app.models import Feed


class FeedSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feed
        fields = (
            "id", "update_date", "releaseTime",
            "title", "link", "description", "feedType", "source"
        )
        load_instance = False
