from app import celery, db
from app.utils.announcement_handler import AnnounceHandler
from app.utils.model_utilities import get_current_date
from app.models import AnnouncementIncomeSheetAnalysis

import logging


logger = logging.getLogger(__name__)


# rate_limit='10/m' means 10 tasks per minute
@celery.task(rate_limit='10/m', ignore_result=True)
def analyze_announcement_incomesheet(feed_id, link, year=2024, season=1):
    announce_handler = AnnounceHandler(link)
    try:
        income_sheet = announce_handler.get_incomesheet_announce()
        print(income_sheet)
        single_season_incomesheet = announce_handler.get_single_season_incomesheet(
            income_sheet, year, season)
        single_season_incomesheet = announce_handler.calculate_income_sheet_annual_growth_rate(
            single_season_incomesheet, year, season)
    except Exception as e:
        single_season_incomesheet = {}
        single_season_incomesheet['processing_failed'] = True
    finally:
        single_season_incomesheet['feed_id'] = feed_id
        single_season_incomesheet['year'] = year
        single_season_incomesheet['season'] = str(season)
        single_season_incomesheet['update_date'] = get_current_date()

    announcement_income_sheet = AnnouncementIncomeSheetAnalysis.query.filter_by(feed_id=feed_id).one_or_none()
    if announcement_income_sheet:
        for key in single_season_incomesheet:
            announcement_income_sheet[key] = single_season_incomesheet[key]
    else:
        announcement_income_sheet = AnnouncementIncomeSheetAnalysis(**single_season_incomesheet)

    try:
        db.session.add(announcement_income_sheet)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(e)

    return single_season_incomesheet