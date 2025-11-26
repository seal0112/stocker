import pytest
from datetime import datetime


from app.utils.stock_screener import StockScreenerManager



@pytest.mark.usefixtures('dev_client')
class TestStockScreener():

    @pytest.mark.parametrize("option", ["月營收近一年次高"])
    @pytest.mark.parametrize("data_date", [datetime(2025, 8, 8)])
    def test_get_revenue_stock_screener(self, option, data_date):
        stock_screener = StockScreenerManager(option, data_date)
        result = stock_screener.screener()
        print(result)
        assert type(result) == list
