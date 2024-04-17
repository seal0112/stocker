from string import Template
from datetime import datetime
import json
import math

from sqlalchemy import text

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

    def screener(self):
        message_list = []
        message = ''
        sql_command = self.screener_format['sqlSyntax'].format(**self.query_condition)

        with db.engine.connect() as conn:
            stocks = conn.execute(text(sql_command)).fetchall()

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

