from sqlalchemy import Column, Integer, String, Date, TEXT, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import datetime

Base = declarative_base()


class Basic_information(Base):
    __tablename__ = 'basic_information'

    id = Column(String(4), primary_key=True, autoincrement=False)
    update_date = Column(
        Date, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d"))
    type = Column(String(3), nullable=False)
    公司名稱 = Column(TEXT, nullable=False)
    公司簡稱 = Column(String(10))
    產業類別 = Column(String(10))
    外國企業註冊地國 = Column(String(10))
    住址 = Column(TEXT)
    營利事業統一編號 = Column(String(8))
    董事長 = Column(String(30))
    總經理 = Column(String(30))
    發言人 = Column(String(30))
    發言人職稱 = Column(String(20))
    代理發言人 = Column(String(30))
    總機電話 = Column(String(30))
    成立日期 = Column(Date)
    上市上櫃興櫃公開發行日期 = Column(Date)
    普通股每股面額 = Column(String(15))
    實收資本額 = Column(BIGINT)
    已發行普通股數或TDR原發行股數 = Column(BIGINT)
    私募普通股 = Column(BIGINT)
    特別股 = Column(BIGINT)
    編製財務報告類型 = Column(String(2))
    普通股盈餘分派或虧損撥補頻率 = Column(String(6))
    普通股年度現金股息及紅利決議層級 = Column(String(3))
    股票過戶機構 = Column(TEXT)
    過戶電話 = Column(String(12))
    過戶地址 = Column(TEXT)
    簽證會計師事務所 = Column(TEXT)
    簽證會計師一 = Column(String(20))
    簽證會計師二 = Column(String(20))
    英文簡稱 = Column(TEXT)
    英文通訊地址 = Column(TEXT)
    傳真機號碼 = Column(String(12))
    電子郵件信箱 = Column(TEXT)
    公司網址 = Column(TEXT)
    投資人關係聯絡人 = Column(String(20))
    投資人關係聯絡人職稱 = Column(String(20))
    投資人關係聯絡電話 = Column(String(12))
    投資人關係聯絡電子郵件 = Column(TEXT)
    公司網站內利害關係人專區網址 = Column(TEXT)
    # Add add a decorator property to serialize data from the database

    @property
    def serialize(self):
        return {
            'id': self['id'],
            'update_date': self['update_date'],
            'type': self['type'],
            '公司名稱': self['公司名稱'],
            '公司簡稱': self['公司簡稱'],
            '產業類別': self['產業類別'],
            '外國企業註冊地國': self['外國企業註冊地國'],
            '住址': self['住址'],
            '營利事業統一編號': self['營利事業統一編號'],
            '董事長': self['董事長'],
            '總經理': self['總經理'],
            '發言人': self['發言人'],
            '發言人職稱': self['發言人職稱'],
            '代理發言人': self['代理發言人'],
            '總機電話': self['總機電話'],
            '成立日期': self['成立日期'],
            '上市上櫃興櫃公開發行日期': self['上市上櫃興櫃公開發行日期'],
            '普通股每股面額': self['普通股每股面額'],
            '實收資本額': self['實收資本額'],
            '已發行普通股數或TDR原發行股數': self['已發行普通股數或TDR原發行股數'],
            '私募普通股': self['私募普通股'],
            '特別股': self['特別股'],
            '編製財務報告類型': self['編製財務報告類型'],
            '普通股盈餘分派或虧損撥補頻率': self['普通股盈餘分派或虧損撥補頻率'],
            '普通股年度現金股息及紅利決議層級': self['普通股年度現金股息及紅利決議層級'],
            '股票過戶機構': self['股票過戶機構'],
            '過戶電話': self['過戶電話'],
            '過戶地址': self['過戶地址'],
            '簽證會計師事務所': self['簽證會計師事務所'],
            '簽證會計師一': self['簽證會計師一'],
            '簽證會計師二': self['簽證會計師二'],
            '英文簡稱': self['英文簡稱'],
            '英文通訊地址': self['英文通訊地址'],
            '傳真機號碼': self['傳真機號碼'],
            '電子郵件信箱': self['電子郵件信箱'],
            '投資人關係聯絡人': self['投資人關係聯絡人'],
            '投資人關係聯絡人職稱': self['投資人關係聯絡人職稱'],
            '投資人關係聯絡電話': self['投資人關係聯絡電話'],
            '投資人關係聯絡電子郵件': self['投資人關係聯絡電子郵件'],
            '公司網站內利害關係人專區網址': self['公司網站內利害關係人專區網址'],
        }


engine = create_engine(
    """mysql+pymysql://newuser:123456@localhost/stocker?charset=utf8""")
Base.metadata.create_all(engine)
