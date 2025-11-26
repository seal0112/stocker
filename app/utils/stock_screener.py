from string import Template
from datetime import datetime
import json
import math
from pathlib import Path
import logging

from sqlalchemy import text
from app.database_setup import BasicInformation
from app.models.recommended_stock import RecommendedStock

from .. import db

logger = logging.getLogger(__name__)


class StockScreenerManager:

    def __init__(self, option, date=datetime.now()):
        self.option = option
        self.screener_format = self.get_screener_format(self.option)
        self.now = date
        month_list = [(10, 11, 12), (1, 2, 3), (4, 5, 6), (7, 8, 9)][math.floor((self.now.month-1)/3)]
        self.query_condition = {
            "date": self.now.strftime('%Y-%m-%d'),
            "season": (math.ceil(self.now.month/3)-2)%4+1,
            "year": self.now.year-1 if (math.ceil(self.now.month/3)-2)%4+1 == 4 else self.now.year,
            "month": (self.now.month-2)%12+1,
            "monthList": month_list
        }

    def get_screener_format(self, option):
        # Get the project root directory (assuming this file is in app/utils/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        config_path = project_root / 'critical_file' / 'screener_format.json'

        try:
            with open(config_path, 'r', encoding='utf-8') as reader:
                config = json.load(reader)
                if option not in config:
                    logger.error(f"Option '{option}' not found in screener_format.json")
                    raise KeyError(f"Invalid screener option: {option}")
                return config[option]
        except FileNotFoundError:
            logger.error(f"Screener format file not found at: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in screener_format.json: {e}")
            raise

    def screener(self) -> list:
        try:
            sql_command = self.screener_format['sqlSyntax'].format(**self.query_condition)
            with db.engine.connect() as conn:
                stocks = conn.execute(text(sql_command)).fetchall()

            logger.info(f"Found {len(stocks)} stocks from initial query")
            filter_stocks = [stock for stock in stocks if self.check_stock_valuation(stock[0])]
            logger.info(f"After valuation check: {len(filter_stocks)} stocks passed")

            if not filter_stocks:
                return []
            else:
                return self.format_screener_message(filter_stocks)
        except Exception as e:
            logger.error(f"Error in screener: {e}", exc_info=True)
            raise

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

    def save_recommended_stock(self, stocks, today=None):
        today = today or self.query_condition['date']
        try:
            for stock in stocks:
                recommended_stock = db.session.query(db.exists().where(
                    db.and_(
                        RecommendedStock.stock_id == stock[0],
                        RecommendedStock.update_date == self.query_condition['date'],
                        RecommendedStock.filter_model == self.option
                    )
                )).scalar()
                if not recommended_stock:
                    new_recommended_stock = RecommendedStock(
                        stock_id=stock[0],
                        update_date=self.query_condition['date'],
                        filter_model=self.option
                    )
                    db.session.add(new_recommended_stock)
            db.session.commit()
            logger.info(f"Successfully saved {len(stocks)} recommended stocks for {self.option}")
        except Exception as ex:
            logger.error(f"Failed to save recommended stocks: {ex}", exc_info=True)
            db.session.rollback()
            raise

    def check_stock_valuation(self, stock_id: str) -> bool:
        """
        Check if the stock valuation is within the acceptable range.
        """
        stock = BasicInformation.query.filter_by(id=stock_id).one_or_none()
        if not stock:
            return False

        # Get required data and check for None early
        last_income_sheet = stock.get_newest_season_income_sheet()
        if not last_income_sheet:
            return False

        average_monthly_price = stock.get_average_monthly_price(3)
        if average_monthly_price is None:
            return False

        # Check if daily_information exists before accessing
        if not stock.daily_information or stock.daily_information.本日收盤價 is None:
            return False

        # Get EPS - use consistent attribute access
        last_income_sheet_eps = getattr(last_income_sheet, '基本每股盈餘', None)
        if last_income_sheet_eps is None or last_income_sheet_eps <= 0.3:
            return False

        # Calculate core business ratio
        營業利益率 = getattr(last_income_sheet, '營業利益率', None)
        稅前淨利率 = getattr(last_income_sheet, '稅前淨利率', None)

        if 營業利益率 is None or 稅前淨利率 is None or 稅前淨利率 == 0:
            return False

        core_business_ratio = 營業利益率 / 稅前淨利率
        if core_business_ratio <= 0.7:
            return False

        # Get PE average
        pe_average = stock.get_pe_quantile(0.5, 5)
        if pe_average is None:
            return False

        # Parse stock price
        try:
            stock_price = float(stock.daily_information.本日收盤價)
        except (ValueError, TypeError):
            return False

        # Final valuation checks
        return (
            stock_price < (average_monthly_price * 1.25) and
            (stock_price / (last_income_sheet_eps * 4)) < pe_average
        )
