import pytest
from datetime import date
from decimal import Decimal

from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis
from app.models.feed import Feed


@pytest.fixture
def mock_announcement_income_sheet_analysis():
    """Fixture to create an AnnouncementIncomeSheetAnalysis instance."""
    return AnnouncementIncomeSheetAnalysis(
        feed_id=1,
        stock_id='2330',
        update_date=date(2024, 3, 15),
        year=2024,
        season='1',
        processing_failed=False,
        營業收入合計=1000000000,
        營業收入合計年增率=10.5,
        營業毛利=300000000,
        營業利益=200000000,
        稅前淨利=180000000,
        本期淨利=150000000,
        基本每股盈餘=5.5
    )


@pytest.mark.usefixtures('test_app')
class TestAnnouncementIncomeSheetAnalysis:
    """Test suite for AnnouncementIncomeSheetAnalysis model."""

    def test_instance_creation(self, mock_announcement_income_sheet_analysis):
        """Test creation of AnnouncementIncomeSheetAnalysis instance."""
        analysis = mock_announcement_income_sheet_analysis
        assert analysis.feed_id == 1
        assert analysis.stock_id == '2330'
        assert analysis.update_date == date(2024, 3, 15)
        assert analysis.year == 2024
        assert analysis.season == '1'
        assert analysis.營業收入合計 == 1000000000
        assert analysis.基本每股盈餘 == 5.5

    def test_getitem_setitem(self, mock_announcement_income_sheet_analysis):
        """Test __getitem__ and __setitem__ methods."""
        analysis = mock_announcement_income_sheet_analysis

        # Test __getitem__
        assert analysis['stock_id'] == '2330'
        assert analysis['營業收入合計'] == 1000000000

        # Test __setitem__
        analysis['營業收入合計'] = 2000000000
        assert analysis['營業收入合計'] == 2000000000

    def test_calculate_ratio(self, test_app, sample_announcement_income_sheet_analysis):
        """Test calculate_ratio method."""
        with test_app.app_context():
            analysis = sample_announcement_income_sheet_analysis

            # Call calculate_ratio
            analysis.calculate_ratio()

            # Verify calculated ratios
            assert analysis.營業毛利率 == 30.0
            assert analysis.營業利益率 == 20.0
            assert analysis.稅前淨利率 == 18.0
            assert analysis.本期淨利率 == 15.0

            # Verify 本業佔比 calculation
            expected_本業佔比 = round((20.0 / 18.0) * 100, 2)
            assert analysis.本業佔比 == expected_本業佔比

    def test_calculate_ratio_zero_revenue(self, test_app, sample_feed):
        """Test calculate_ratio with zero revenue."""
        with test_app.app_context():
            from app import db

            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                營業收入合計=0,
                營業毛利=100000,
                營業利益=50000,
                稅前淨利=30000,
                本期淨利=20000
            )
            db.session.add(analysis)
            db.session.commit()

            # Call calculate_ratio
            analysis.calculate_ratio()

            # All ratios should be None when revenue is zero
            assert analysis.營業毛利率 is None
            assert analysis.營業利益率 is None
            assert analysis.稅前淨利率 is None
            assert analysis.本期淨利率 is None

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_calculate_ratio_zero_pretax_profit(self, test_app, sample_feed):
        """Test calculate_ratio with zero pretax profit."""
        with test_app.app_context():
            from app import db

            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                營業收入合計=1000000,
                營業毛利=300000,
                營業利益=200000,
                稅前淨利=100000,
                本期淨利=80000
            )
            db.session.add(analysis)
            db.session.commit()

            # Set 稅前淨利率 to 0
            analysis.稅前淨利率 = 0
            analysis.calculate_ratio()

            # 本業佔比 should be 0 when 稅前淨利率 is 0
            assert analysis.本業佔比 == 0

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_database_operations(self, test_app, sample_feed):
        """Test database CRUD operations."""
        with test_app.app_context():
            from app import db

            # Create
            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                update_date=date(2024, 6, 15),
                year=2024,
                season='2',
                營業收入合計=2000000000,
                基本每股盈餘=6.5
            )
            db.session.add(analysis)
            db.session.commit()

            # Read
            retrieved = AnnouncementIncomeSheetAnalysis.query.filter_by(
                feed_id=sample_feed.id
            ).first()
            assert retrieved is not None
            assert retrieved.stock_id == '2330'
            assert retrieved.season == '2'

            # Update
            retrieved.基本每股盈餘 = 7.0
            db.session.commit()

            updated = AnnouncementIncomeSheetAnalysis.query.filter_by(
                feed_id=sample_feed.id
            ).first()
            assert updated.基本每股盈餘 == 7.0

            # Delete
            db.session.delete(updated)
            db.session.commit()

            deleted = AnnouncementIncomeSheetAnalysis.query.filter_by(
                feed_id=sample_feed.id
            ).first()
            assert deleted is None

    def test_foreign_key_relationship_with_feed(self, test_app, sample_feed):
        """Test foreign key relationship with Feed."""
        with test_app.app_context():
            from app import db

            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                update_date=date.today(),
                year=2024,
                season='1'
            )
            db.session.add(analysis)
            db.session.commit()

            # Test relationship
            feed = Feed.query.filter_by(id=sample_feed.id).first()
            assert feed is not None
            assert feed.announcement_income_sheet_analysis is not None
            assert feed.announcement_income_sheet_analysis.feed_id == sample_feed.id

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_foreign_key_relationship_with_basic_info(
        self, test_app, sample_announcement_income_sheet_analysis, sample_basic_info
    ):
        """Test foreign key relationship with BasicInformation."""
        with test_app.app_context():
            from app.database_setup import BasicInformation

            analysis = sample_announcement_income_sheet_analysis

            # Query through relationship
            basic_info = BasicInformation.query.filter_by(id=analysis.stock_id).first()
            assert basic_info is not None
            assert basic_info.id == '2330'

    def test_query_by_date(self, test_app, sample_feed):
        """Test querying by update_date."""
        with test_app.app_context():
            from app import db

            today = date.today()

            # Create test data
            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                update_date=today,
                year=2024,
                season='1'
            )
            db.session.add(analysis)
            db.session.commit()

            # Query by date
            results = AnnouncementIncomeSheetAnalysis.query.filter_by(
                update_date=today
            ).all()

            assert len(results) >= 1
            assert any(r.feed_id == sample_feed.id for r in results)

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_query_by_stock_id(self, test_app, sample_feed):
        """Test querying by stock_id."""
        with test_app.app_context():
            from app import db

            # Create test data
            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id='2330',
                update_date=date.today(),
                year=2024,
                season='1'
            )
            db.session.add(analysis)
            db.session.commit()

            # Query by stock_id
            results = AnnouncementIncomeSheetAnalysis.query.filter_by(
                stock_id='2330'
            ).all()

            assert len(results) >= 1
            assert all(r.stock_id == '2330' for r in results)

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_query_by_year_and_season(self, test_app, sample_feed):
        """Test querying by year and season."""
        with test_app.app_context():
            from app import db

            # Create test data
            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                update_date=date.today(),
                year=2024,
                season='3'
            )
            db.session.add(analysis)
            db.session.commit()

            # Query by year and season
            results = AnnouncementIncomeSheetAnalysis.query.filter_by(
                year=2024,
                season='3'
            ).all()

            assert len(results) >= 1
            assert any(r.feed_id == sample_feed.id for r in results)

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_processing_failed_flag(self, test_app, sample_feed):
        """Test processing_failed flag."""
        with test_app.app_context():
            from app import db

            # Create analysis with processing_failed=True
            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                update_date=date.today(),
                processing_failed=True
            )
            db.session.add(analysis)
            db.session.commit()

            # Query failed processing
            failed = AnnouncementIncomeSheetAnalysis.query.filter_by(
                processing_failed=True
            ).all()

            assert len(failed) >= 1
            assert any(f.feed_id == sample_feed.id for f in failed)

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_decimal_precision(self, test_app, sample_feed):
        """Test decimal field precision."""
        with test_app.app_context():
            from app import db

            # Create analysis with decimal values
            analysis = AnnouncementIncomeSheetAnalysis(
                feed_id=sample_feed.id,
                stock_id=sample_feed.stock_id,
                營業毛利率=12.345,
                基本每股盈餘=5.678
            )
            db.session.add(analysis)
            db.session.commit()

            # Retrieve and check precision (should be rounded to 2 decimal places)
            retrieved = AnnouncementIncomeSheetAnalysis.query.filter_by(
                feed_id=sample_feed.id
            ).first()

            # The database stores as Numeric(10, 2)
            assert retrieved.營業毛利率 == Decimal('12.35')
            assert retrieved.基本每股盈餘 == Decimal('5.68')

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()
