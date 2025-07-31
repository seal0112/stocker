from marshmallow import fields

from app import ma
from app.models import Feed


class FeedSchema(ma.Schema):
    class Meta:
        model = Feed
        fields = (
            "id", "update_date", "releaseTime",
            "title", "link", "description", "feedType", "source"
        )
