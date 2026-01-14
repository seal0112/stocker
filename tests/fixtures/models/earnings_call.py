"""EarningsCall model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
- Teardown runs before sample_basic_info teardown (pytest handles this)
"""
import pytest
from datetime import date
from app import db
from app.earnings_call.models import EarningsCall


@pytest.fixture
def sample_earnings_call(sample_basic_info):
    """Create sample earnings call for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
    earnings_call = EarningsCall(
        stock_id=sample_basic_info.id,
        meeting_date=date(2024, 4, 18),
        meeting_end_date=date(2024, 4, 18),
        location='台北市中山區松江路',
        description='2024年第一季法人說明會',
        file_name_chinese='2330_2024Q1法說會'
    )
    db.session.add(earnings_call)
    db.session.commit()

    yield earnings_call

    # Explicit cleanup
    EarningsCall.query.filter_by(
        stock_id=sample_basic_info.id,
        meeting_date=date(2024, 4, 18)
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_earnings_call_list(sample_basic_info):
    """Create multiple earnings calls for testing.

    Depends on: sample_basic_info → app_context
    """
    calls = []
    for quarter in range(1, 5):
        call = EarningsCall(
            stock_id=sample_basic_info.id,
            meeting_date=date(2023, quarter * 3 + 1, 18),
            meeting_end_date=date(2023, quarter * 3 + 1, 18),
            location='台北市中山區松江路',
            description=f'2023年第{quarter}季法人說明會',
            file_name_chinese=f'2330_2023Q{quarter}法說會'
        )
        calls.append(call)
        db.session.add(call)
    db.session.commit()

    yield calls

    # Explicit cleanup
    EarningsCall.query.filter_by(
        stock_id=sample_basic_info.id
    ).filter(EarningsCall.meeting_date >= date(2023, 1, 1)).filter(
        EarningsCall.meeting_date < date(2024, 1, 1)
    ).delete()
    db.session.commit()
