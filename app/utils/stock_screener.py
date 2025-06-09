from string import Template
from datetime import datetime
import json
import math

from sqlalchemy import text
from app.database_setup import BasicInformation

from .. import db


class StockScrennerManager:

    def __init__(self, option):
        self.option = option
        self.screener_format = self.getScreenerFormat(self.option)
        self.now = datetime.now()
        month_list = [(10, 11, 12), (1, 2, 3), (4, 5, 6), (7, 8, 9)][math.floor((self.now.month-1)/3)]
        self.query_condition = {
            "date": self.now.strftime('%Y-%m-%d'),
            "season": (math.ceil(self.now.month/3)-2)%4+1,
            "year": self.now.year-1 if (math.ceil(self.now.month/3)-2)%4+1 == 4 else self.now.year,
            "month": (self.now.month-2)%12+1,
            "monthList": month_list
        }

    def getScreenerFormat(self, option):
        with open('./critical_file/screener_format.json') as reader:
            return json.loads(reader.read())[option]

    def screener(self) -> list:
        sql_command = self.screener_format['sqlSyntax'].format(**self.query_condition)
        with db.engine.connect() as conn:
            stocks = conn.execute(text(sql_command)).fetchall()
        filter_stocks = [stock for stock in stocks if self.check_stock_valuation(stock[0])]
        if not filter_stocks:
            return []
        else:
            return self.format_screener_message(filter_stocks)

    def format_screener_message(self, stocks) -> list:
        message_list = []
        message = ''
        for idx, stock in enumerate(stocks):
            if int(idx) % 10 == 0:
                message_list.append(message)
                message = self.screener_format['title'].format(
                    option=self.option, page=(idx//10)+1, **self.query_condition)
            message += '\n{}'.format(self.screener_format['content'].format(*stock))
        else:
            message_list.append(message)
        message_list.pop(0)
        return message_list

    def check_stock_valuation(self, stock_id: str) -> bool:
        """
        Check if the stock valuation is within the acceptable range.
        """
        stock = BasicInformation.query.filter_by(id=stock_id).one_or_none()
        if not stock:
            return False

        last_income_sheet = stock.get_newest_season_income_sheet()
        average_monthly_price = stock.get_average_monthly_price(3)
        last_income_sheet_eps = last_income_sheet['基本每股盈餘']

        if (
            last_income_sheet.營業利益率 is not None and
            last_income_sheet.稅前淨利率 and
            last_income_sheet.稅前淨利率 != 0
        ):
            core_business_ratio = last_income_sheet.營業利益率 / last_income_sheet.稅前淨利率
        else:
            core_business_ratio = None
        pe_average = stock.get_pe_quantile(0.5, 5)

        if (
            last_income_sheet_eps is None or
            pe_average is None or
            core_business_ratio is None or
            average_monthly_price is None or
            not stock.daily_information or
            stock.daily_information.本日收盤價 is None
        ):
            return False

        try:
            stock_price = float(stock.daily_information.本日收盤價)
        except Exception:
            return False

        return (
            last_income_sheet_eps > 0.3 and
            core_business_ratio > 0.7 and
            stock_price < (average_monthly_price * 1.25) and
            (stock_price / (last_income_sheet_eps * 4)) < pe_average
        )
