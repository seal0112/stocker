"""Unit tests for app/tasks."""
import pytest
from unittest.mock import MagicMock, patch, call

from app import db
from app.models import AnnouncementIncomeSheetAnalysis
from app.tasks.test_task.tasks import add
from app.tasks.feed_task.tasks import analyze_announcement_incomesheet


# ---------------------------------------------------------------------------
# test_task
# ---------------------------------------------------------------------------

class TestAdd:
    def test_returns_sum(self):
        assert add(1, 2) == 3

    def test_zero(self):
        assert add(0, 0) == 0

    def test_negative(self):
        assert add(-3, 1) == -2


# ---------------------------------------------------------------------------
# feed_task — analyze_announcement_incomesheet
# ---------------------------------------------------------------------------

FAKE_INCOME_SHEET = {'revenue': 1000, 'gross_profit': 300}
FAKE_SINGLE_SEASON = {'revenue': 1000, 'gross_profit': 300, 'yoy': 0.1}
FAKE_WITH_GROWTH = {'revenue': 1000, 'gross_profit': 300, 'yoy': 0.1, 'qoq': 0.05}


@pytest.fixture
def mock_announce_handler():
    with patch('app.tasks.feed_task.tasks.AnnounceHandler') as MockClass:
        handler = MagicMock()
        handler.get_incomesheet_announce.return_value = FAKE_INCOME_SHEET
        handler.get_single_season_incomesheet.return_value = FAKE_SINGLE_SEASON
        handler.calculate_income_sheet_annual_growth_rate.return_value = FAKE_WITH_GROWTH
        MockClass.return_value = handler
        yield handler


class TestAnalyzeAnnouncementIncomesheet:
    def test_returns_result_dict(self, mock_announce_handler, app_context):
        with patch('app.tasks.feed_task.tasks.AnnouncementIncomeSheetAnalysis') as MockModel:
            MockModel.query.filter_by.return_value.one_or_none.return_value = None
            instance = MagicMock()
            MockModel.return_value = instance

            result = analyze_announcement_incomesheet(feed_id=1, link='http://example.com', year=2024, season=1)

        assert result['feed_id'] == 1
        assert result['year'] == 2024
        assert result['season'] == '1'
        assert 'update_date' in result

    def test_creates_new_record_when_not_exists(self, mock_announce_handler, app_context):
        with patch('app.tasks.feed_task.tasks.AnnouncementIncomeSheetAnalysis') as MockModel:
            MockModel.query.filter_by.return_value.one_or_none.return_value = None
            instance = MagicMock()
            MockModel.return_value = instance

            with patch('app.tasks.feed_task.tasks.db') as mock_db:
                analyze_announcement_incomesheet(feed_id=1, link='http://example.com')
                mock_db.session.add.assert_called_once_with(instance)
                mock_db.session.commit.assert_called_once()

    def test_updates_existing_record(self, mock_announce_handler, app_context):
        existing = MagicMock()
        with patch('app.tasks.feed_task.tasks.AnnouncementIncomeSheetAnalysis') as MockModel:
            MockModel.query.filter_by.return_value.one_or_none.return_value = existing

            with patch('app.tasks.feed_task.tasks.db') as mock_db:
                analyze_announcement_incomesheet(feed_id=1, link='http://example.com')
                mock_db.session.add.assert_called_once_with(existing)
                mock_db.session.commit.assert_called_once()

    def test_sets_processing_failed_on_handler_error(self, app_context):
        with patch('app.tasks.feed_task.tasks.AnnounceHandler') as MockClass:
            handler = MagicMock()
            handler.get_incomesheet_announce.side_effect = Exception('Network error')
            MockClass.return_value = handler

            with patch('app.tasks.feed_task.tasks.AnnouncementIncomeSheetAnalysis') as MockModel:
                MockModel.query.filter_by.return_value.one_or_none.return_value = None
                MockModel.return_value = MagicMock()

                with patch('app.tasks.feed_task.tasks.db'):
                    result = analyze_announcement_incomesheet(feed_id=99, link='http://bad.com')

        assert result['processing_failed'] is True
        assert result['feed_id'] == 99

    def test_rollbacks_on_db_error(self, mock_announce_handler, app_context):
        with patch('app.tasks.feed_task.tasks.AnnouncementIncomeSheetAnalysis') as MockModel:
            MockModel.query.filter_by.return_value.one_or_none.return_value = None
            MockModel.return_value = MagicMock()

            with patch('app.tasks.feed_task.tasks.db') as mock_db:
                mock_db.session.commit.side_effect = Exception('DB error')
                analyze_announcement_incomesheet(feed_id=1, link='http://example.com')
                mock_db.session.rollback.assert_called_once()
