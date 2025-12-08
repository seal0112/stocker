from .. import ma


class MonthRevenueSchema(ma.Schema):
    """Schema for MonthRevenue with essential revenue fields."""
    class Meta:
        fields = (
            "id", "stock_id", "year", "month", "update_date",
            "當月營收", "上月營收", "去年當月營收",
            "上月比較增減", "去年同月增減",
            "當月累計營收", "去年累計營收", "前期比較增減",
            "備註"
        )
