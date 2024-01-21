from bs4 import BeautifulSoup
import requests
import re
from ..database_setup import IncomeSheet


class AnnounceHandler:

    def __init__(self, announce_link):
        self.announce_link = announce_link
        self.data_key = ['營業收入合計', '營業毛利', '營業利益', '稅前淨利', '本期淨利', '母公司業主淨利', '基本每股盈餘']
        self.ratio_key = ['營業毛利', '營業利益', '稅前淨利', '本期淨利']

    def get_incomesheet_announce(self):
        res = requests.get(self.announce_link)
        soup = BeautifulSoup(res.text, 'html.parser')
        result = soup.findChildren('table')[4].findChildren('tr')[17].findChildren('td')[0].findChildren('font')[0].text.split('\n')

        income_sheet = {
            '營業收入合計': None,
            '營業毛利': None,
            '營業毛利率': None,
            '營業利益': None,
            '營業利益率': None,
            '稅前淨利': None,
            '稅前淨利率': None,
            '本期淨利': None,
            '本期淨利率': None,
            '母公司業主淨利': None,
            '基本每股盈餘': None,
        }
        for i in range(4, 11):
            data = re.sub(r'[\u4e00-\u9fa5]', '', re.sub(r'[\,\$]', '', re.sub(r'\(\D*\)', '', result[i]))).split(':')[1].strip()
            data = float('-' + re.sub(r'[\(\)]', '', data)) if re.search(r'\(\d+\.*\d*\)', data) else float(data)
            income_sheet[self.data_key[i-4]] = data
        return income_sheet

    def get_single_season_incomesheet(self, income_sheet, year, season):
        stock_id = self.announce_link.split('&')[6].split('=')[1]
        income_sheet['stock_id'] = stock_id
        data = IncomeSheet.query.filter_by(stock_id=stock_id, year=year).all()
        for d in data:
            if d.season >= season:
                continue
            past_income_sheet = d.serialize
            for key in self.data_key:
                income_sheet[key] = income_sheet[key] - past_income_sheet[key]
        # 下面計算各種比率，除Q1,Q3, 要先撈前幾季的資料剪掉數字後再算
        for key in self.ratio_key:
            income_sheet[key+'率'] = str(round(income_sheet[key] / income_sheet['營業收入合計'], 4)*100) + '%'

        return income_sheet
