# test_database_setup.py

import pytest
from datetime import date
from app.database_setup import BasicInformation
from app.utils.model_utilities import get_current_date


@pytest.fixture
def basic_information_instance():
    """Fixture to create a BasicInformation instance."""
    return BasicInformation(
        id="123456",
        update_date=get_current_date(),
        exchange_type="sii",
        公司名稱="測試公司",
        公司簡稱="測試",
        產業類別="科技",
        外國企業註冊地國="台灣",
        住址="台北市",
        營利事業統一編號="12345678",
        董事長="王小明",
        總經理="李小華",
        發言人="陳大明",
        發言人職稱="經理",
        代理發言人="張小美",
        總機電話="02-12345678",
        成立日期="2000-01-01",
        上市上櫃興櫃公開發行日期="2005-01-01",
        普通股每股面額="10",
        實收資本額=100000000,
        已發行普通股數或TDR原發行股數=10000000,
        私募普通股=0,
        特別股=0,
        編製財務報告類型="A",
        普通股盈餘分派或虧損撥補頻率="年度",
        普通股年度現金股息及紅利決議層級="董事會",
        股票過戶機構="測試過戶機構",
        過戶電話="02-87654321",
        過戶地址="新北市",
        簽證會計師事務所="測試會計師事務所",
        簽證會計師一="會計師甲",
        簽證會計師二="會計師乙",
        英文簡稱="Test Corp",
        英文通訊地址="Taipei, Taiwan",
        傳真機號碼="02-12345679",
        電子郵件信箱="test@example.com",
        公司網址="http://www.test.com",
        投資人關係聯絡人="投資人甲",
        投資人關係聯絡人職稱="專員",
        投資人關係聯絡電話="02-12345680",
        投資人關係聯絡電子郵件="investor@test.com",
        公司網站內利害關係人專區網址="http://www.test.com/stakeholders"
    )


@pytest.mark.usefixtures("basic_information_instance")
class TestBasicInformation:

    def test_instance_creation(self, basic_information_instance):
        """Test creation of BasicInformation instance."""
        assert basic_information_instance.id == "123456"
        assert basic_information_instance.公司名稱 == "測試公司"
        assert basic_information_instance.實收資本額 == 100000000

    def test_serialize(self, basic_information_instance):
        """Test the serialize property."""
        serialized_data = basic_information_instance.serialize
        assert isinstance(serialized_data, dict)
        assert serialized_data["id"] == "123456"
        assert serialized_data["公司名稱"] == "測試公司"

    def test_getitem(self, basic_information_instance):
        """Test __getitem__ method."""
        assert basic_information_instance["公司名稱"] == "測試公司"
        assert basic_information_instance["實收資本額"] == 100000000

    def test_setitem(self, basic_information_instance):
        """Test __setitem__ method."""
        basic_information_instance["公司名稱"] = "新測試公司"
        assert basic_information_instance.公司名稱 == "新測試公司"

    def test_default_update_date(self, test_app):
        """Test default value for update_date when saved to database."""
        from app import db

        basic_info = BasicInformation(
            id="999998",
            公司名稱="測試預設日期",
            公司簡稱="測試"
        )
        db.session.add(basic_info)
        db.session.commit()

        # Refresh to get the default value from database
        db.session.refresh(basic_info)
        # Compare date objects (database returns date, get_current_date returns string)
        assert basic_info.update_date == date.today()

        # Cleanup
        db.session.delete(basic_info)
        db.session.commit()

    def test_exchange_type_valid_values(self):
        """Test exchange_type accepts valid enum values."""
        valid_types = ['sii', 'otc', 'rotc', 'pub', 'delist']
        for exchange_type in valid_types:
            basic_info = BasicInformation(
                id="999999",
                公司名稱="測試",
                exchange_type=exchange_type
            )
            assert basic_info.exchange_type == exchange_type


class TestBasicInformationDatabase:
    """Tests that require database interaction."""

    def test_save_and_retrieve(self, test_app, sample_basic_info):
        """Test saving and retrieving BasicInformation from database."""
        from app import db
        from app.database_setup import BasicInformation

        retrieved = db.session.query(BasicInformation).filter_by(
            id=sample_basic_info.id
        ).one_or_none()

        assert retrieved is not None
        assert retrieved.id == sample_basic_info.id
        assert retrieved.公司名稱 == sample_basic_info.公司名稱

    def test_relationship_with_daily_information(self, test_app, sample_basic_info, sample_daily_info):
        """Test relationship between BasicInformation and DailyInformation."""
        from app import db
        from app.database_setup import BasicInformation

        # Query fresh instance to get relationship
        stock = db.session.query(BasicInformation).filter_by(
            id=sample_basic_info.id
        ).one_or_none()

        assert stock is not None
        assert stock.daily_information is not None
        assert stock.daily_information.stock_id == sample_basic_info.id

    def test_cascade_delete(self, test_app):
        """Test cascade delete removes related DailyInformation."""
        from app import db
        from app.database_setup import BasicInformation, DailyInformation
        from datetime import date

        # Create stock with daily info
        stock = BasicInformation(
            id='9999',
            公司名稱='測試刪除',
            公司簡稱='測試',
            exchange_type='sii'
        )
        db.session.add(stock)
        db.session.commit()

        daily_info = DailyInformation(
            stock_id='9999',
            update_date=date.today(),
            本日收盤價=100.0
        )
        db.session.add(daily_info)
        db.session.commit()

        # Verify daily info exists
        assert db.session.query(DailyInformation).filter_by(stock_id='9999').one_or_none() is not None

        # Delete stock
        db.session.delete(stock)
        db.session.commit()

        # Verify daily info is also deleted
        assert db.session.query(DailyInformation).filter_by(stock_id='9999').one_or_none() is None