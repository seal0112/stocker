import pytest
from datetime import date

from app.earnings_call.earnings_call_services import EarningsCallService


earnings_call_service = EarningsCallService()


@pytest.mark.usefixtures('client')
class TestEarningsCallService():

    @pytest.mark.skip(reason="not implemented")
    def test_create_earnings_call(self):
        assert 1 == 1

    @pytest.mark.parametrize("stock_id", ["2330", "2454", "5474"])
    @pytest.mark.parametrize("meeting_date", [date.today().strftime('%Y-%m-%d')])
    def test_get_stock_all_earnings_call(self, stock_id, meeting_date):
        earnings_calls = earnings_call_service.get_stock_all_earnings_call(stock_id, meeting_date)
        assert type(earnings_calls) == list

    @pytest.mark.skip(reason="not implemented")
    def test_get_earnings_call(self):
        pass

    @pytest.mark.skip(reason="not implemented")
    def test_update_earnings_call(self):
        pass

    @pytest.mark.skip(reason="not implemented")
    def test_delete_earnings_call(self):
        pass
