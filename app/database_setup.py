from datetime import datetime, time
from . import db


# db.Index('revenue_idx_stock', Month_Revenue.stock_id)

def getCurrentDate():
    return datetime.now().strftime("%Y-%m-%d")


basicInformationAndFeed = db.Table('basicInformation_feed',
                             db.Column(
                                'basic_information_id',
                                db.String(6),
                                db.ForeignKey('basic_information.id'),
                                primary_key=True),
                             db.Column(
                                'feed_id',
                                db.Integer,
                                db.ForeignKey('feed.id'),
                                primary_key=True)
                          )


# done
class Basic_Information(db.Model):
    __tablename__ = 'basic_information'

    id = db.Column(db.String(6), primary_key=True, autoincrement=False)
    update_date = db.Column(
        db.Date, nullable=False,
        default=getCurrentDate)
    exchange_type = db.Column(
        db.Enum('sii', 'otc', 'rotc', 'pub', 'delist'))
    公司名稱 = db.Column(db.Text, nullable=False)
    公司簡稱 = db.Column(db.String(10), index=True)
    產業類別 = db.Column(db.String(10))
    外國企業註冊地國 = db.Column(db.String(10))
    住址 = db.Column(db.Text)
    營利事業統一編號 = db.Column(db.String(8))
    董事長 = db.Column(db.String(50))
    總經理 = db.Column(db.String(50))
    發言人 = db.Column(db.String(50))
    發言人職稱 = db.Column(db.String(20))
    代理發言人 = db.Column(db.String(50))
    總機電話 = db.Column(db.String(30))
    成立日期 = db.Column(db.String(10))
    上市上櫃興櫃公開發行日期 = db.Column(db.String(10))
    普通股每股面額 = db.Column(db.String(15))
    實收資本額 = db.Column(db.BigInteger)
    已發行普通股數或TDR原發行股數 = db.Column(db.BigInteger)
    私募普通股 = db.Column(db.BigInteger)
    特別股 = db.Column(db.BigInteger)
    編製財務報告類型 = db.Column(db.String(2))
    普通股盈餘分派或虧損撥補頻率 = db.Column(db.String(6))
    普通股年度現金股息及紅利決議層級 = db.Column(db.String(3))
    股票過戶機構 = db.Column(db.Text)
    過戶電話 = db.Column(db.String(30))
    過戶地址 = db.Column(db.Text)
    簽證會計師事務所 = db.Column(db.Text)
    簽證會計師一 = db.Column(db.String(20))
    簽證會計師二 = db.Column(db.String(20))
    英文簡稱 = db.Column(db.Text)
    英文通訊地址 = db.Column(db.Text)
    傳真機號碼 = db.Column(db.String(30))
    電子郵件信箱 = db.Column(db.Text)
    公司網址 = db.Column(db.Text)
    投資人關係聯絡人 = db.Column(db.String(50))
    投資人關係聯絡人職稱 = db.Column(db.String(30))
    投資人關係聯絡電話 = db.Column(db.String(30))
    投資人關係聯絡電子郵件 = db.Column(db.Text)
    公司網站內利害關係人專區網址 = db.Column(db.Text)
    feeds = db.relationship(
        'Feed',
        secondary=basicInformationAndFeed,
        backref=db.backref('basic_information', lazy=True),
        lazy='dynamic')


    # Add add a decorator property to serialize data from the datadb.Model
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


# db.Index('basic_infomation_name_idx', Basic_Information.公司簡稱)


# done
class Balance_Sheet(db.Model):
    __tablename__ = 'balance_sheet'

    id = db.Column(db.Integer, primary_key=True)
    update_date = db.Column(
        db.Date, nullable=False,
        default=getCurrentDate)
    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    season = db.Column(
        db.Enum('1', '2', '3', '4'), nullable=False)
    現金及約當現金 = db.Column(db.BigInteger)
    透過其他綜合損益按公允價值衡量之金融資產流動 = db.Column(db.BigInteger)
    透過損益按公允價值衡量之金融資產流動 = db.Column(db.BigInteger)
    按攤銷後成本衡量之金融資產流動 = db.Column(db.BigInteger)
    存貨 = db.Column(db.BigInteger)
    應收帳款淨額 = db.Column(db.BigInteger)
    應收票據淨額 = db.Column(db.BigInteger)
    流動資產合計 = db.Column(db.BigInteger)
    透過其他綜合損益按公允價值衡量之金融資產非流動 = db.Column(db.BigInteger)
    透過損益按公允價值衡量之金融資產非流動 = db.Column(db.BigInteger)
    按攤銷後成本衡量之金融資產非流動 = db.Column(db.BigInteger)
    採用權益法之投資 = db.Column(db.BigInteger)
    不動產廠房及設備 = db.Column(db.BigInteger)
    無形資產 = db.Column(db.BigInteger)
    非流動資產合計 = db.Column(db.BigInteger)
    資產總計 = db.Column(db.BigInteger)
    短期借款 = db.Column(db.BigInteger)
    一年或一營業週期內到期長期負債 = db.Column(db.BigInteger)
    應付帳款 = db.Column(db.BigInteger)
    應付票據 = db.Column(db.BigInteger)
    流動負債合計 = db.Column(db.BigInteger)
    長期借款 = db.Column(db.BigInteger)
    應付公司債 = db.Column(db.BigInteger)
    非流動負債合計 = db.Column(db.BigInteger)
    負債總計 = db.Column(db.BigInteger)
    股本合計 = db.Column(db.BigInteger)
    資本公積合計 = db.Column(db.BigInteger)
    保留盈餘合計 = db.Column(db.BigInteger)
    非控制權益 = db.Column(db.BigInteger)
    歸屬於母公司業主之權益 = db.Column(db.BigInteger)
    權益總計 = db.Column(db.BigInteger)
    負債及權益總計 = db.Column(db.BigInteger)

    # Add add a decorator property to serialize data from the datadb.Model
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


# prototype done
class Cash_Flow(db.Model):
    __tablename__ = 'cashflow'

    id = db.Column(db.Integer, primary_key=True)
    update_date = db.Column(
        db.Date, nullable=False,
        default=getCurrentDate)
    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    season = db.Column(
        db.Enum('1', '2', '3', '4'), nullable=False)
    停業單位稅前淨利淨損 = db.Column(db.BigInteger)
    繼續營業單位稅前淨利淨損 = db.Column(db.BigInteger)
    本期稅前淨利淨損 = db.Column(db.BigInteger)
    折舊費用 = db.Column(db.BigInteger)
    攤銷費用 = db.Column(db.BigInteger)
    利息收入 = db.Column(db.BigInteger)
    利息費用 = db.Column(db.BigInteger)
    退還支付所得稅 = db.Column(db.BigInteger)
    營業活動之淨現金流入流出 = db.Column(db.BigInteger)
    取得處分不動產廠房及設備 = db.Column(db.BigInteger)
    取得處分無形資產 = db.Column(db.BigInteger)
    投資活動之淨現金流入流出 = db.Column(db.BigInteger)
    現金增資 = db.Column(db.BigInteger)
    現金減資 = db.Column(db.BigInteger)
    庫藏股現金增減 = db.Column(db.BigInteger)
    發放現金股利 = db.Column(db.BigInteger)
    償還公司債 = db.Column(db.BigInteger)
    發行公司債 = db.Column(db.BigInteger)
    籌資活動之淨現金流入流出 = db.Column(db.BigInteger)
    期初現金及約當現金餘額 = db.Column(db.BigInteger)
    期末現金及約當現金餘額 = db.Column(db.BigInteger)
    本期現金及約當現金增加減少數 = db.Column(db.BigInteger)

    # Add add a decorator property to serialize data from the datadb.Model
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


# prototype done
class Income_Sheet(db.Model):
    __tablename__ = 'income_sheet'

    id = db.Column(db.Integer, primary_key=True)
    update_date = db.Column(
        db.Date, nullable=False,
        default=getCurrentDate)
    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    season = db.Column(
        db.Enum('1', '2', '3', '4'), nullable=False)
    營業收入合計 = db.Column(db.BigInteger)
    營業成本合計 = db.Column(db.BigInteger)
    營業毛利 = db.Column(db.BigInteger)
    營業毛利率 = db.Column(db.Numeric(13, 2))
    推銷費用 = db.Column(db.BigInteger)
    推銷費用率 = db.Column(db.Numeric(13, 2))
    管理費用 = db.Column(db.BigInteger)
    管理費用率 = db.Column(db.Numeric(13, 2))
    研究發展費用 = db.Column(db.BigInteger)
    研究發展費用率 = db.Column(db.Numeric(13, 2))
    營業費用 = db.Column(db.BigInteger)
    營業費用率 = db.Column(db.Numeric(13, 2))
    營業利益 = db.Column(db.BigInteger)
    營業利益率 = db.Column(db.Numeric(13, 2))
    營業外收入及支出合計 = db.Column(db.BigInteger)
    稅前淨利 = db.Column(db.BigInteger)
    稅前淨利率 = db.Column(db.Numeric(13, 2))
    所得稅費用 = db.Column(db.BigInteger)
    所得稅費用率 = db.Column(db.Numeric(13, 2))
    本期淨利 = db.Column(db.BigInteger)
    本期淨利率 = db.Column(db.Numeric(13, 2))
    母公司業主淨利 = db.Column(db.BigInteger)
    基本每股盈餘 = db.Column(db.Float)
    稀釋每股盈餘 = db.Column(db.Float)

    # Add add a decorator property to serialize data from the datadb.Model
    @property
    def serialize(self):
        res = {}
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            res[attr] = val
        return res

    def __repr__(self):
        return "%s: %s: %s: %s" % (
            self.id, self.stock_id, self.year, self.season)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

# done
class Month_Revenue(db.Model):
    __tablename__ = 'month_revenue'

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(
        db.Enum('1', '2', '3', '4', '5', '6',
                '7', '8', '9', '10', '11', '12'), nullable=False)
    update_date = db.Column(
        db.Date, nullable=False,
        default=getCurrentDate)
    當月營收 = db.Column(db.BigInteger)
    上月營收 = db.Column(db.BigInteger)
    去年當月營收 = db.Column(db.BigInteger)
    上月比較增減 = db.Column(db.Float)
    去年同月增減 = db.Column(db.Float)
    當月累計營收 = db.Column(db.BigInteger)
    去年累計營收 = db.Column(db.BigInteger)
    前期比較增減 = db.Column(db.Float)
    備註 = db.Column(db.Text)
    basic_information = db.relationship(Basic_Information)

    # Add add a decorator property to serialize data from the datadb.Model
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


class Daily_Information(db.Model):
    __tablename__ = 'daily_information'

    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'),
        primary_key=True, nullable=False)
    update_date = db.Column(
        db.Date, nullable=False,
        default=getCurrentDate)
    本日收盤價 = db.Column(db.Float)
    本日漲跌 = db.Column(db.Float)
    近四季每股盈餘 = db.Column(db.Float)
    本益比 = db.Column(db.Numeric(13, 2))
    殖利率 = db.Column(db.Float)
    股價淨值比 = db.Column(db.Float)

    # Add add a decorator property to serialize data from the datadb.Model
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


class Stock_Commodity(db.Model):
    __tablename__ = 'stock_commodity'

    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'),
        primary_key=True, nullable=False)
    stock_future = db.Column(db.Boolean, nullable=False, default=False)
    stock_option = db.Column(db.Boolean, nullable=False,  default=False)
    small_stock_future = db.Column(db.Boolean, nullable=False,  default=False)

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


class Data_Update_Date(db.Model):
    __tablename__ = 'data_update_date'

    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'),
        primary_key=True, nullable=False)
    month_revenue_last_update = db.Column(db.Date, nullable=True)
    announcement_last_update = db.Column(db.Date, nullable=True)
    news_last_update = db.Column(db.Date, nullable=True)
    income_sheet_last_update = db.Column(db.Date, nullable=True)


feedsAndfeedsTags = db.Table('feed_feedTag',
                             db.Column('feed_id', db.Integer, db.ForeignKey(
                                 'feed.id'), primary_key=True),
                             db.Column('feedTag', db.Integer, db.ForeignKey(
                                 'feed_tag.id'), primary_key=True)
                             )


class Feed(db.Model):
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True)
    update_date = db.Column(
        db.Date, nullable=False, default=getCurrentDate)
    releaseTime = db.Column(db.DateTime, nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(600), nullable=False, unique=True)
    source = db.Column(db.String(20), default='mops')
    description = db.Column(db.Text)
    feedType = db.Column(
        db.Enum('announcement', 'news'),
        nullable=False, default='announcement')
    tags = db.relationship(
        'FeedTag', secondary=feedsAndfeedsTags,
        lazy='joined', backref=db.backref('feed'))
    stocks = db.relationship(
        'Basic_Information',
        secondary=basicInformationAndFeed)

    @property
    def serialize(self):
        res = {}
        tags = []
        stocks = []
        for attr, val in self.__dict__.items():
            if attr == '_sa_instance_state':
                continue
            else:
                res[attr] = val
        if self.tags:
            tags = [tag.name for tag in self.tags]
        res['tags'] = tags
        if self.stocks:
            stocks = [stock.id for stock in self.stocks]
        res['stocks'] = stocks
        return res

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class FeedTag(db.Model):
    __tablename__ = 'feed_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name
        }


class PushNotification(db.Model):
    __tablename__ = 'push_notification'

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'),
        primary_key=True, nullable=False)
    notify_enabled = db.Column(db.Boolean, default=False)
    line_notify_token = db.Column(db.String(64), nullable=True)
    notify_time = db.Column(db.Time, default=time(hour=20, minute=0))
    notify_news = db.Column(db.Boolean, default=False)
    notify_announcement = db.Column(db.Boolean, default=False)
    notify_month_revenue = db.Column(db.Boolean, default=False)
    notify_income_sheet = db.Column(db.Boolean, default=False)


class StockSearchCounts(db.Model):
    __tablename__ = 'stock_search_counts'

    stock_id = db.Column(
        db.String(6), db.ForeignKey('basic_information.id'),
        primary_key=True, nullable=False)
    search_count = db.Column(db.Integer, default=0)
