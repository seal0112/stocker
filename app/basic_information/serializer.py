from .. import ma


class BasicInformationSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "公司簡稱", "exchange_type"
        )