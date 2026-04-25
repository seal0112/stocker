import pytest
from pathlib import Path


TEST_SCREENER_FORMAT_PATH = Path(__file__).parent.parent / 'fixtures' / 'screener_format.json'


@pytest.fixture(autouse=True)
def patch_screener_format_path(monkeypatch):
    """Use test fixture screener_format.json instead of critical_file/ in tests."""
    monkeypatch.setenv('SCREENER_FORMAT_PATH', str(TEST_SCREENER_FORMAT_PATH))
