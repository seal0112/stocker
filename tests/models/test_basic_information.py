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