from .. import ma


class IncomeSheetSchema(ma.Schema):
    """Schema for IncomeSheet with essential financial fields."""
    class Meta:
        fields = (
            "id", "stock_id", "year", "season", "update_date",
            "營業收入合計", "營業成本合計", "營業毛利", "營業毛利率",
            "營業費用", "營業費用率", "營業利益", "營業利益率",
            "稅前淨利", "稅前淨利率", "本期淨利", "本期淨利率",
            "基本每股盈餘", "稀釋每股盈餘"
        )
