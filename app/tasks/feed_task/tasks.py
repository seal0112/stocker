from app import celery, db
from app.utils.announcement_handler import AnnounceHandler
from app.database_setup import AnnouncementIncomeSheetAnalysis
from app.utils.model_utilities import get_current_date

import logging

logger = logging.getLogger()


# rate_limit='10/m' means 10 tasks per minute
@celery.task(rate_limit='10/m', ignore_result=True)
def analyze_announcement_incomesheet(feed_id, link, year=2024, season=1):
    announce_handler = AnnounceHandler(link)
    income_sheet = announce_handler.get_incomesheet_announce()
    single_season_incomesheet = announce_handler.get_single_season_incomesheet(
        income_sheet, year, season)
    single_season_incomesheet = announce_handler.calculate_income_sheet_annual_growth_rate(
        single_season_incomesheet, year, season)

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