import requests
import re
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from ..database_setup import IncomeSheet


class AnnounceHandler:

    def __init__(self, announce_link=None):
        self.announce_link = announce_link
        self.data_key = ['營業收入合計', '營業毛利', '營業利益', '稅前淨利', '本期淨利', '母公司業主淨利', '基本每股盈餘']
        self.ratio_key = ['營業毛利', '營業利益', '稅前淨利', '本期淨利']
        self.annual_growth_rate_key = ['營業收入合計', '營業毛利率', '營業利益率', '稅前淨利率', '本期淨利率', '基本每股盈餘']

    def _extract_stock_id(self):
        params = parse_qs(urlparse(self.announce_link).query)
        for param_name in ('co_id', 'stock_id', 'StockID'):
            if param_name in params:
                return params[param_name][0]
        raise ValueError(f"Cannot extract stock_id from link: {self.announce_link}")

    def _parse_value(self, raw):
        raw = re.sub(r'\(\D+\)', '', raw)           # remove unit annotations like (千元)
        raw = re.sub(r'[,\$]', '', raw)             # remove commas and dollar signs
        raw = re.sub(r'[一-龥]', '', raw).strip()  # remove Chinese characters
        if not raw:
            return None
        if re.search(r'\(\d+\.?\d*\)', raw):        # negative number expressed as (1234)
            return float('-' + re.sub(r'[()]', '', raw))
        return float(raw)

    def get_incomesheet_announce(self):
        res = requests.get(self.announce_link)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Search for the font element containing '營業收入合計' instead of relying
        # on hard-coded table/row indices which break when MOPS page structure changes.
        target_text = None
        for font in soup.find_all('font'):
            if '營業收入合計' in font.text:
                target_text = font.text
                break

        if target_text is None:
            raise ValueError("Cannot find income sheet data on the announcement page")

        announcement_income_sheet = {
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

        for line in target_text.split('\n'):
            for key in self.data_key:
                if key in line:
                    # Support both half-width ':' (U+003A) and full-width '：' (U+FF1A)
                    parts = re.split(r'[:：]', line, maxsplit=1)
                    if len(parts) < 2:
                        break
                    try:
                        announcement_income_sheet[key] = self._parse_value(parts[1])
                    except (ValueError, IndexError):
                        pass
                    break

        return announcement_income_sheet

    def get_single_season_incomesheet(self, announcement_income_sheet, year, season):
        announcement_income_sheet['stock_id'] = self._extract_stock_id()
        data = IncomeSheet.query.filter_by(stock_id=announcement_income_sheet["stock_id"], year=year).all()
        for d in data:
            if int(d.season) >= int(season):
                continue
            past_income_sheet = d.serialize
            for key in self.data_key:
                announcement_income_sheet[key] = announcement_income_sheet[key] - past_income_sheet[key]
        # 下面計算各種比率，除Q1,Q3, 要先撈前幾季的資料剪掉數字後再算
        for key in self.ratio_key:
            announcement_income_sheet[key+'率'] = round((announcement_income_sheet[key] / announcement_income_sheet['營業收入合計'])*100 , 2)

        # 營業利益率/稅前利益率
        if announcement_income_sheet['稅前淨利率'] not in [0, None]:
            announcement_income_sheet['本業佔比'] = announcement_income_sheet['營業利益率'] / announcement_income_sheet['稅前淨利率'] * 100

        return announcement_income_sheet

    def calculate_income_sheet_annual_growth_rate(self, announcement_income_sheet, year, season):
        last_year = year - 1
        last_year_income_sheet = IncomeSheet.query.filter_by(
            stock_id=announcement_income_sheet["stock_id"], year=last_year, season=season).one_or_none()

        for key in self.annual_growth_rate_key:
            if last_year_income_sheet is None or announcement_income_sheet[key] < 0:
                announcement_income_sheet[key+'年增率'] = None
            else:
                announcement_income_sheet[key+'年增率'] = round(
                    ((announcement_income_sheet[key] / float(last_year_income_sheet[key]))-1)*100 , 2
                )

        return announcement_income_sheet
