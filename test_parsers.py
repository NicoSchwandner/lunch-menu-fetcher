"""
Parser regression checks. Run with `python test_parsers.py` (or `pytest`).

Every restaurant has broken at least once by restyling its page, so each parser
is checked against real snapshots of *both* the current and an older layout.
"""
from datetime import datetime

import pytz

from local.mock.bror_och_bord_html_mock import get_html_text as bror_och_bord_html
from local.mock.gabys_html_mock import get_html_text as gabys_html
from local.mock.gabys_html_mock import get_html_text_legacy as gabys_legacy_html
from local.mock.hildas_json_mock import get_json_text as hildas_json
from src.restaurants.bror_och_bord import extract_bror_och_bord_menu_sections
from src.restaurants.gabys import extract_gabys_menu_sections
from src.restaurants.hildas import extract_menu_items, format_menu_data
from src.utils.weekday import CurrentWeekday, plain_weekday_index

import logging

LOGGER = logging.getLogger("test")

# The snapshots are from week 34 (2026) and week 48 (2024) respectively.
CURRENT_WEEK_DAY = CurrentWeekday(override_time=datetime(2026, 8, 19, 12, tzinfo=pytz.UTC))  # Wed
LEGACY_WEEK_DAY = CurrentWeekday(override_time=datetime(2024, 11, 26, 12, tzinfo=pytz.UTC))  # Tue


def section_for(sections, weekday):
    matching = [s for s in sections if weekday.matches(s['heading'])]
    assert len(matching) == 1, f"expected one section for {weekday}, got {[s['heading'] for s in sections]}"
    return matching[0]


def test_gabys_current_layout():
    sections, error = extract_gabys_menu_sections(LOGGER, gabys_html(), CURRENT_WEEK_DAY)
    assert error is None, error

    today = section_for(sections, CURRENT_WEEK_DAY)
    assert len(today['items']) == 3, today
    assert today['items'][0].startswith("Polentastekt fisk")

    salad = [s for s in sections if 'salad' in s['heading'].lower()]
    assert salad and salad[0]['items'], sections

    # Opening hours ("Wednesday - Saturday: 17:00 - 22:30") must not leak in.
    assert not any(':' in item and len(item) < 20 for s in sections for item in s['items']), sections


def test_gabys_legacy_layout():
    sections, error = extract_gabys_menu_sections(LOGGER, gabys_legacy_html(), LEGACY_WEEK_DAY)
    assert error is None, error
    assert len(section_for(sections, LEGACY_WEEK_DAY)['items']) == 3, sections


def test_gabys_reports_error_when_menu_missing():
    sections, error = extract_gabys_menu_sections(LOGGER, "<html><body><p>Stängt</p></body></html>", CURRENT_WEEK_DAY)
    assert sections is None and error


def test_bror_och_bord_has_all_five_weekdays():
    sections, error = extract_bror_och_bord_menu_sections(LOGGER, bror_och_bord_html())
    assert error is None, error

    weekdays = [plain_weekday_index(s['heading']) for s in sections if s['items']]
    assert [d for d in weekdays if d is not None] == [0, 1, 2, 3, 4], [s['heading'] for s in sections]

    monday = sections[1]
    assert monday['items'][0].startswith("Wallenbergare"), monday
    assert "Färdiga sallader" in monday['items'], monday


def test_hildas_menu_for_today():
    items, category = extract_menu_items(LOGGER, hildas_json(), LEGACY_WEEK_DAY)
    assert items, category

    formatted = format_menu_data(items, category)
    assert formatted['sections'][0]['heading']
    assert all(formatted['sections'][0]['items']), formatted
    assert not any('\r' in item or '\n' in item for item in formatted['sections'][0]['items'])


def test_weekday_matching_rejects_ranges():
    wednesday = CURRENT_WEEK_DAY
    assert wednesday.matches("Onsdag")
    assert wednesday.matches("Wednesday 19/8")
    assert not wednesday.matches("Wednesday – Saturday:")
    assert not wednesday.matches("Lunch is served Monday to Friday")
    assert plain_weekday_index("Måndag 25/8") == 0
    assert plain_weekday_index("Sunday – Tusedays") is None


if __name__ == '__main__':
    failures = 0
    for name, test in sorted(globals().items()):
        if not name.startswith('test_'):
            continue
        try:
            test()
            print(f"PASS {name}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {name}: {e}")
    raise SystemExit(1 if failures else 0)
