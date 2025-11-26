"""Business logic for recommended stocks."""
import logging
from datetime import date, timedelta
from typing import List, Optional, Dict

from app import db
from app.models.recommended_stock import RecommendedStock
from app.database_setup import BasicInformation
from app.utils.model_utilities import get_current_date

logger = logging.getLogger(__name__)


class RecommendedStockService:
    """Service class for recommended stock operations."""

    def get_recommended_stocks(
        self,
        date: Optional[date] = None,
        filter_model: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[RecommendedStock]:
        """
        Get recommended stocks with optional filters.

        Args:
            date: Date to query (default: today)
            filter_model: Filter model name to query
            limit: Maximum number of results

        Returns:
            List of RecommendedStock objects
        """
        try:
            query = db.session.query(RecommendedStock)

            # Filter by date
            if date:
                query = query.filter(RecommendedStock.update_date == date)
            else:
                query = query.filter(RecommendedStock.update_date == get_current_date())

            # Filter by model
            if filter_model:
                query = query.filter(RecommendedStock.filter_model == filter_model)

            # Order by update_date desc, then id
            query = query.order_by(
                RecommendedStock.update_date.desc(),
                RecommendedStock.id.desc()
            )

            # Apply limit
            if limit:
                query = query.limit(limit)

            return query.all()

        except Exception as e:
            logger.error(f"Error getting recommended stocks: {e}", exc_info=True)
            raise

    def get_recommended_stock_by_id(self, stock_id: int) -> Optional[RecommendedStock]:
        """
        Get a specific recommended stock by ID.

        Args:
            stock_id: RecommendedStock ID

        Returns:
            RecommendedStock object or None
        """
        try:
            return RecommendedStock.query.filter_by(id=stock_id).first()
        except Exception as e:
            logger.error(f"Error getting recommended stock {stock_id}: {e}", exc_info=True)
            raise

    def get_stocks_by_stock_id(
        self,
        stock_id: str,
        days: int = 30
    ) -> List[RecommendedStock]:
        """
        Get recommendation history for a specific stock.

        Args:
            stock_id: Stock ID (e.g., '2330')
            days: Number of days to look back

        Returns:
            List of RecommendedStock objects
        """
        try:
            cutoff_date = get_current_date() - timedelta(days=days)

            return RecommendedStock.query.filter(
                RecommendedStock.stock_id == stock_id,
                RecommendedStock.update_date >= cutoff_date
            ).order_by(RecommendedStock.update_date.desc()).all()

        except Exception as e:
            logger.error(f"Error getting recommendation history for {stock_id}: {e}", exc_info=True)
            raise

    def get_available_filter_models(self) -> List[str]:
        """
        Get list of all available filter models.

        Returns:
            List of unique filter model names
        """
        try:
            results = db.session.query(
                RecommendedStock.filter_model
            ).distinct().all()

            return [r[0] for r in results]

        except Exception as e:
            logger.error(f"Error getting filter models: {e}", exc_info=True)
            raise

    def get_statistics(self, date: Optional[date] = None) -> Dict:
        """
        Get statistics for recommended stocks.

        Args:
            date: Date to query (default: today)

        Returns:
            Dictionary with statistics
        """
        try:
            target_date = date or get_current_date()

            query = RecommendedStock.query.filter_by(update_date=target_date)
            total_count = query.count()

            # Count by filter model
            model_counts = {}
            for model in self.get_available_filter_models():
                count = query.filter_by(filter_model=model).count()
                if count > 0:
                    model_counts[model] = count

            return {
                'date': target_date.isoformat(),
                'total_recommendations': total_count,
                'by_filter_model': model_counts
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}", exc_info=True)
            raise

    def create_recommendation(self, data: Dict) -> RecommendedStock:
        """
        Create a new recommendation.

        Args:
            data: Dictionary with stock_id, update_date, filter_model

        Returns:
            Created RecommendedStock object
        """
        try:
            # Check if stock exists
            stock = BasicInformation.query.filter_by(id=data['stock_id']).first()
            if not stock:
                raise ValueError(f"Stock {data['stock_id']} not found")

            # Check for duplicates
            existing = RecommendedStock.query.filter_by(
                stock_id=data['stock_id'],
                update_date=data.get('update_date', get_current_date()),
                filter_model=data['filter_model']
            ).first()

            if existing:
                logger.warning(f"Recommendation already exists: {existing}")
                return existing

            # Create new recommendation
            recommendation = RecommendedStock(
                stock_id=data['stock_id'],
                update_date=data.get('update_date', get_current_date()),
                filter_model=data['filter_model']
            )

            db.session.add(recommendation)
            db.session.commit()

            logger.info(f"Created recommendation: {recommendation}")
            return recommendation

        except Exception as e:
            logger.error(f"Error creating recommendation: {e}", exc_info=True)
            db.session.rollback()
            raise

    def delete_recommendation(self, recommendation_id: int) -> bool:
        """
        Delete a recommendation.

        Args:
            recommendation_id: ID of recommendation to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            recommendation = RecommendedStock.query.filter_by(id=recommendation_id).first()

            if not recommendation:
                return False

            db.session.delete(recommendation)
            db.session.commit()

            logger.info(f"Deleted recommendation: {recommendation_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting recommendation {recommendation_id}: {e}", exc_info=True)
            db.session.rollback()
            raise
