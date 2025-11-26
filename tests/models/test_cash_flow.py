import pytest
from datetime import date

from app.database_setup import CashFlow, BasicInformation


@pytest.fixture
def mock_cash_flow():
    """Fixture to create a CashFlow instance."""
    return CashFlow(
        stock_id='2330',
        year=2024,
        season='3',
        update_date=date(2024, 11, 14),
        停業單位稅前淨利淨損=0,
        繼續營業單位稅前淨利淨損=2200000000,
        本期稅前淨利淨損=2200000000,
        折舊費用=800000000,
        攤銷費用=50000000,
        利息收入=30000000,
        利息費用=15000000,
        退還支付所得稅=330000000,
        營業活動之淨現金流入流出=2500000000,
        取得處分不動產廠房及設備=-1200000000,
        取得處分無形資產=-80000000,
        投資活動之淨現金流入流出=-1500000000,
        現金增資=0,
        現金減資=0,
        庫藏股現金增減=0,
        發放現金股利=-800000000,
        償還公司債=0,
        發行公司債=0,
        籌資活動之淨現金流入流出=-800000000,
        期初現金及約當現金餘額=1300000000,
        期末現金及約當現金餘額=1500000000,
        本期現金及約當現金增加減少數=200000000
    )


@pytest.mark.usefixtures('test_app')
class TestCashFlow:
    """Test suite for CashFlow model."""

    def test_instance_creation(self, mock_cash_flow):
        """Test creation of CashFlow instance."""
        assert mock_cash_flow.stock_id == '2330'
        assert mock_cash_flow.year == 2024
        assert mock_cash_flow.season == '3'
        assert mock_cash_flow.本期稅前淨利淨損 == 2200000000
        assert mock_cash_flow.營業活動之淨現金流入流出 == 2500000000
        assert mock_cash_flow.投資活動之淨現金流入流出 == -1500000000
        assert mock_cash_flow.籌資活動之淨現金流入流出 == -800000000

    def test_cash_flow_reconciliation(self, mock_cash_flow):
        """Test that cash flow changes reconcile correctly."""
        # 現金變動 = 營業 + 投資 + 籌資
        total_change = (
            mock_cash_flow.營業活動之淨現金流入流出 +
            mock_cash_flow.投資活動之淨現金流入流出 +
            mock_cash_flow.籌資活動之淨現金流入流出
        )
        assert total_change == mock_cash_flow.本期現金及約當現金增加減少數

        # 期末 = 期初 + 本期變動
        expected_ending = (
            mock_cash_flow.期初現金及約當現金餘額 +
            mock_cash_flow.本期現金及約當現金增加減少數
        )
        assert expected_ending == mock_cash_flow.期末現金及約當現金餘額

    def test_serialize(self, mock_cash_flow):
        """Test the serialize property."""
        serialized = mock_cash_flow.serialize
        assert isinstance(serialized, dict)
        assert serialized['stock_id'] == '2330'
        assert serialized['year'] == 2024
        assert serialized['營業活動之淨現金流入流出'] == 2500000000

    def test_getitem(self, mock_cash_flow):
        """Test __getitem__ method."""
        assert mock_cash_flow['營業活動之淨現金流入流出'] == 2500000000
        assert mock_cash_flow['投資活動之淨現金流入流出'] == -1500000000

    def test_setitem(self, mock_cash_flow):
        """Test __setitem__ method."""
        mock_cash_flow['營業活動之淨現金流入流出'] = 3000000000
        assert mock_cash_flow.營業活動之淨現金流入流出 == 3000000000

    def test_database_operations(self, test_app, sample_basic_info):
        """Test database CRUD operations."""
        with test_app.app_context():
            from app import db

            # Create
            cash_flow = CashFlow(
                stock_id=sample_basic_info.id,
                year=2024,
                season='3',
                營業活動之淨現金流入流出=2500000000,
                投資活動之淨現金流入流出=-1500000000,
                籌資活動之淨現金流入流出=-800000000
            )
            db.session.add(cash_flow)
            db.session.commit()

            # Read
            retrieved = CashFlow.query.filter_by(
                stock_id='2330',
                year=2024,
                season='3'
            ).first()
            assert retrieved is not None
            assert retrieved.營業活動之淨現金流入流出 == 2500000000

            # Cleanup
            db.session.delete(retrieved)
            db.session.commit()

    def test_operating_cash_flow_positive(self, mock_cash_flow):
        """Test that operating cash flow is positive (healthy sign)."""
        assert mock_cash_flow.營業活動之淨現金流入流出 > 0

    def test_investing_cash_flow_negative(self, mock_cash_flow):
        """Test investing cash flow (negative means investing in growth)."""
        assert mock_cash_flow.投資活動之淨現金流入流出 < 0

    def test_free_cash_flow_calculation(self, mock_cash_flow):
        """Test calculation of free cash flow."""
        # Free Cash Flow = Operating Cash Flow - Capital Expenditures
        # 取得處分不動產廠房及設備 is negative when purchasing
        capex = abs(mock_cash_flow.取得處分不動產廠房及設備)
        free_cash_flow = mock_cash_flow.營業活動之淨現金流入流出 - capex

        assert free_cash_flow == 1300000000  # 2500M - 1200M

    def test_multiple_seasons(self, test_app, sample_basic_info):
        """Test storing multiple seasons of cash flow data."""
        with test_app.app_context():
            from app import db

            # Create data for all 4 seasons
            for season in ['1', '2', '3', '4']:
                cash_flow = CashFlow(
                    stock_id=sample_basic_info.id,
                    year=2024,
                    season=season,
                    營業活動之淨現金流入流出=1000000000 * int(season),
                    投資活動之淨現金流入流出=-500000000 * int(season),
                    籌資活動之淨現金流入流出=-200000000 * int(season)
                )
                db.session.add(cash_flow)
            db.session.commit()

            # Query all seasons
            all_seasons = CashFlow.query.filter_by(
                stock_id='2330',
                year=2024
            ).order_by(CashFlow.season).all()

            assert len(all_seasons) == 4
            assert all_seasons[2].season == '3'
            assert all_seasons[2].營業活動之淨現金流入流出 == 3000000000

            # Cleanup
            CashFlow.query.filter_by(stock_id='2330').delete()
            db.session.commit()
