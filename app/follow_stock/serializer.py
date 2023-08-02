from .. import ma

from ..basic_information.serializer import BasicInformationSchema


class FollowStockSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "stock", "last_update_time",
            "comment", "long_or_short"
        )

    stock = ma.Nested(BasicInformationSchema)