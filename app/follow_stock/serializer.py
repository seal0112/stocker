from .. import ma

from ..basic_information.serializer import BasicInformationSchema
from .models import Follow_Stock


class FollowStockSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Follow_Stock
        fields = (
            "id", "stock", "last_update_time",
            "comment", "long_or_short"
        )
        load_instance = False

    stock = ma.Nested(BasicInformationSchema)