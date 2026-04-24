from .. import ma
from ..database_setup import MonthRevenue


class MonthRevenueSchema(ma.SQLAlchemyAutoSchema):
    """Schema for MonthRevenue with essential revenue fields."""
    class Meta:
        model = MonthRevenue
        fields = (
            "id", "stock_id", "year", "month", "update_date",
            "當月營收", "上月營收", "去年當月營收",
            "上月比較增減", "去年同月增減",
            "當月累計營收", "去年累計營收", "前期比較增減",
            "備註"
        )
        load_instance = False
        include_fk = True
