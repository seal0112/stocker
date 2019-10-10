from sqlalchemy import Column, ForeignKey
from sqlalchemy import Date, Enum, Integer, String, TEXT
from sqlalchemy import BIGINT, Float, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import enum
import datetime
import json

Base = declarative_base()

with open('./critical_flie/databaseAccount.json') as accountReader:
    dbAccount = json.loads(accountReader.read())


class Basic_information(Base):
    __tablename__ = 'basic_information'

    id = Column(String(6), primary_key=True, autoincrement=False)
    update_date = Column(
        Date, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d"))
    type = Column(Enum('sii', 'otc', 'rotc', 'pub'), nullable=False)
    公司名稱 = Column(TEXT, nullable=False)
    公司簡稱 = Column(String(10))
    產業類別 = Column(String(10))
    外國企業註冊地國 = Column(String(10))
    住址 = Column(TEXT)
    營利事業統一編號 = Column(String(8))
    董事長 = Column(String(50))
    總經理 = Column(String(50))
    發言人 = Column(String(50))
    發言人職稱 = Column(String(20))
    代理發言人 = Column(String(50))
    總機電話 = Column(String(30))
    成立日期 = Column(String(10))
    上市上櫃興櫃公開發行日期 = Column(String(10))
    普通股每股面額 = Column(String(15))
    實收資本額 = Column(BIGINT)
    已發行普通股數或TDR原發行股數 = Column(BIGINT)
    私募普通股 = Column(BIGINT)
    特別股 = Column(BIGINT)
    編製財務報告類型 = Column(String(2))
    普通股盈餘分派或虧損撥補頻率 = Column(String(6))
    普通股年度現金股息及紅利決議層級 = Column(String(3))
    股票過戶機構 = Column(TEXT)
    過戶電話 = Column(String(30))
    過戶地址 = Column(TEXT)
    簽證會計師事務所 = Column(TEXT)
    簽證會計師一 = Column(String(20))
    簽證會計師二 = Column(String(20))
    英文簡稱 = Column(TEXT)
    英文通訊地址 = Column(TEXT)
    傳真機號碼 = Column(String(30))
    電子郵件信箱 = Column(TEXT)
    公司網址 = Column(TEXT)
    投資人關係聯絡人 = Column(String(50))
    投資人關係聯絡人職稱 = Column(String(20))
    投資人關係聯絡電話 = Column(String(30))
    投資人關係聯絡電子郵件 = Column(TEXT)
    公司網站內利害關係人專區網址 = Column(TEXT)

    # Add add a decorator property to serialize data from the database
    @property
    def serialize(self):
        res = {}
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            res[attr] = val
        return res

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Cashflow(Base):
    __tablename__ = 'cashflow'

    id = Column(Integer, primary_key=True)
    update_date = Column(
        Date, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d"))
    stock_id = Column(
        String(6), ForeignKey('basic_information.id'), nullable=False)
    year = Column(Integer, nullable=False)
    season = Column(
        Enum('1', '2', '3', '4'), nullable=False)
    折舊費用 = Column(BIGINT, default=0)
    攤銷費用 = Column(BIGINT, default=0)
    營業活動之淨現金流入 = Column(BIGINT, nullable=False)
    資本支出= Column(BIGINT, default=0)
    不動產廠房及設備轉列費用數 = Column(BIGINT, default=0)
    取得不動產廠房及設備 = Column(BIGINT, default=0)
    處分不動產廠房及設備 = Column(BIGINT, default=0)
    取得不動產及設備 = Column(BIGINT, default=0)
    處分不動產及設備 = Column(BIGINT, default=0)
    取得投資性不動產 = Column(BIGINT, default=0)
    處分投資性不動產 = Column(BIGINT, default=0)
    投資性不動產公允價值調整損失 = Column(BIGINT, default=0)
    處分及報廢不動產廠房及設備損失 = Column(BIGINT, default=0)
    處分投資性不動產損失 = Column(BIGINT, default=0)
    無形資產金流 = Column(BIGINT, default=0)
    取得無形資產 = Column(BIGINT, default=0)
    處分無形資產 = Column(BIGINT, default=0)
    處分無形資產損失 = Column(BIGINT, default=0)
    投資活動之淨現金流入 = Column(BIGINT, nullable=False)
    籌資活動之淨現金流入 = Column(BIGINT, nullable=False)
    本期現金及約當現金增加數 = Column(BIGINT, nullable=False)

    # Add add a decorator property to serialize data from the database
    @property
    def serialize(self):
        res = {}
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            res[attr] = val
        return res

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Income_sheet(Base):
    __tablename__ = 'income_sheet'

    id = Column(Integer, primary_key=True)
    update_date = Column(
        Date, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d"))
    stock_id = Column(
        String(6), ForeignKey('basic_information.id'), nullable=False)
    year = Column(Integer, nullable=False)
    season = Column(
        Enum('1', '2', '3', '4'), nullable=False)
    營業收入合計 = Column(BIGINT)
    營業成本合計 = Column(BIGINT)
    營業毛利 = Column(BIGINT)
    營業毛利率 = Column(Float)
    推銷費用 = Column(BIGINT)
    推銷費用率 = Column(Float)
    管理費用 = Column(BIGINT)
    管理費用率 = Column(Float)
    研究發展費用 = Column(BIGINT)
    研究發展費用率 = Column(Float)
    營業費用 = Column(BIGINT)
    營業費用率 = Column(Float)
    營業利益 = Column(BIGINT)
    營業利益率 = Column(Float)
    營業外收入及支出合計 = Column(BIGINT)
    稅前淨利 = Column(BIGINT)
    稅前淨利率 = Column(Float)
    所得稅費用 = Column(BIGINT)
    所得稅費用率 = Column(Float)
    本期淨利 = Column(BIGINT)
    本期淨利率 = Column(Float)
    基本每股盈餘 = Column(Float)
    稀釋每股盈餘 = Column(Float)

    # Add add a decorator property to serialize data from the database
    @property
    def serialize(self):
        res = {}
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            res[attr] = val
        return res

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Month_revenue(Base):
    __tablename__ = 'month_revenue'

    id = Column(Integer, primary_key=True)
    stock_id = Column(
        String(6), ForeignKey('basic_information.id'), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(
        Enum('1', '2', '3', '4', '5', '6',
             '7', '8', '9', '10', '11', '12'), nullable=False)
    update_date = Column(
        Date, nullable=False,
        default=datetime.datetime.now().strftime("%Y-%m-%d"))
    當月營收 = Column(BIGINT)
    上月營收 = Column(BIGINT)
    去年當月營收 = Column(BIGINT)
    上月比較增減 = Column(Float)
    去年同月增減 = Column(Float)
    當月累計營收 = Column(BIGINT)
    去年累計營收 = Column(BIGINT)
    前期比較增減 = Column(Float)
    備註 = Column(TEXT)
    basic_information = relationship(Basic_information)

    # Add add a decorator property to serialize data from the database
    @property
    def serialize(self):
        res = {}
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            res[attr] = val
        return res

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


engine = create_engine(
    """mysql+pymysql://%s:%s@%s/stocker?charset=utf8""" % (
        dbAccount["username"], dbAccount["password"], dbAccount["ip"]))
Base.metadata.create_all(engine)
