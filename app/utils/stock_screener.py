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

    def save_recommended_stock(self, stocks) -> dict:
        """
        Save recommended stocks to database with bulk operations for better performance.

        Args:
            stocks: List of stock tuples from screener results

        Returns:
            dict: Statistics with keys 'added', 'skipped', 'total'
        """
        if not stocks:
            logger.warning("No stocks to save")
            return {"added": 0, "skipped": 0, "total": 0}

        try:
            # Extract stock IDs from the result tuples
            stock_ids = [stock[0] for stock in stocks]
            update_date = self.query_condition['date']

            # Bulk query existing records to avoid N+1 problem
            existing_stocks = db.session.query(RecommendedStock.stock_id).filter(
                db.and_(
                    RecommendedStock.stock_id.in_(stock_ids),
                    RecommendedStock.update_date == update_date,
                    RecommendedStock.filter_model == self.option
                )
            ).all()

            existing_stock_ids = {stock.stock_id for stock in existing_stocks}

            # Prepare new records for bulk insert
            new_stocks = []
            for stock_id in stock_ids:
                if stock_id not in existing_stock_ids:
                    new_stocks.append(RecommendedStock(
                        stock_id=stock_id,
                        update_date=update_date,
                        filter_model=self.option
                    ))

            # Bulk insert new records
            if new_stocks:
                db.session.bulk_save_objects(new_stocks)
                db.session.commit()
                logger.info(
                    f"Saved {len(new_stocks)} new recommended stocks for '{self.option}' "
                    f"on {update_date} (skipped {len(existing_stock_ids)} existing)"
                )
            else:
                logger.info(f"All {len(stocks)} stocks already exist for '{self.option}' on {update_date}")

            return {
                "added": len(new_stocks),
                "skipped": len(existing_stock_ids),
                "total": len(stocks)
            }

        except Exception as ex:
            logger.error(f"Failed to save recommended stocks: {ex}", exc_info=True)
            db.session.rollback()
            raise

    def run_and_save(self) -> dict:
        """
        Complete workflow: run screener and save results to database.

        Returns:
            dict: Results with 'messages' (formatted messages) and 'save_stats' (save statistics)
        """
        logger.info(f"Starting screener workflow for '{self.option}' on {self.query_condition['date']}")

        # Get raw stock data
        sql_command = self.screener_format['sqlSyntax'].format(**self.query_condition)
        with db.engine.connect() as conn:
            stocks = conn.execute(text(sql_command)).fetchall()

        if not stocks:
            logger.info(f"No stocks found for '{self.option}'")
            return {"messages": [], "save_stats": {"added": 0, "skipped": 0, "total": 0}}

        # Filter stocks
        logger.info(f"Found {len(stocks)} stocks, applying valuation checks...")
        filter_stocks = [stock for stock in stocks if self.check_stock_valuation(stock[0])]
        logger.info(f"{len(filter_stocks)} stocks passed valuation checks")

        if not filter_stocks:
            return {"messages": [], "save_stats": {"added": 0, "skipped": 0, "total": 0}}

        # Save to database
        save_stats = self.save_recommended_stock(filter_stocks)

        # Format messages
        messages = self.format_screener_message(filter_stocks)

        return {
            "messages": messages,
            "save_stats": save_stats,
            "stock_count": len(filter_stocks)
        }

    @staticmethod
    def get_recommended_stocks(date=None, filter_model=None):
        """
        Retrieve recommended stocks from database.

        Args:
            date: Date to query (default: today)
            filter_model: Filter model name (default: all models)

        Returns:
            list: RecommendedStock objects
        """
        from app.utils.model_utilities import get_current_date

        query = db.session.query(RecommendedStock)

        if date:
            query = query.filter(RecommendedStock.update_date == date)
        else:
            query = query.filter(RecommendedStock.update_date == get_current_date())

        if filter_model:
            query = query.filter(RecommendedStock.filter_model == filter_model)

        return query.all()

    @staticmethod
    def cleanup_old_recommendations(days_to_keep=90):
        """
        Delete old recommended stock records.

        Args:
            days_to_keep: Number of days to keep (default: 90)

        Returns:
            int: Number of records deleted
        """
        from datetime import timedelta
        from app.utils.model_utilities import get_current_date

        cutoff_date = get_current_date() - timedelta(days=days_to_keep)

        try:
            deleted = db.session.query(RecommendedStock).filter(
                RecommendedStock.update_date < cutoff_date
            ).delete()
            db.session.commit()
            logger.info(f"Cleaned up {deleted} old recommendation records before {cutoff_date}")
            return deleted
        except Exception as ex:
            logger.error(f"Failed to cleanup old recommendations: {ex}", exc_info=True)
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
