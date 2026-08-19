import re
from datetime import datetime
from enum import Enum
from typing import Optional, Set
import pytz
from config import TIMEZONE

class Weekdays(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

SWEDISH_NAMES = {
    0: 'Måndag',
    1: 'Tisdag',
    2: 'Onsdag',
    3: 'Torsdag',
    4: 'Fredag',
    5: 'Lördag',
    6: 'Söndag'
}

ENGLISH_NAMES = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

# Every weekday name in both languages, lowercase. Used to recognise menu
# headings by their text instead of by the markup the restaurant happens to use.
WEEKDAY_INDEX_BY_NAME = {
    name.lower(): index
    for names in (SWEDISH_NAMES, ENGLISH_NAMES)
    for index, name in names.items()
}
ALL_WEEKDAY_NAMES = list(WEEKDAY_INDEX_BY_NAME)

# "Monday", "Måndag:", "Måndag 25/8" - a day heading, not a sentence or a range.
_PLAIN_WEEKDAY_PATTERN = re.compile(
    r"^(?P<name>[^\W\d_]+)[\s:.,\-–—]*(\d{1,2}[\s/.\-]*\d{0,4})?$"
)


def weekday_indices_in(text: str) -> Set[int]:
    """Weekday numbers mentioned anywhere in the text, in either language."""
    lowered = (text or "").lower()
    return {index for name, index in WEEKDAY_INDEX_BY_NAME.items() if name in lowered}


def plain_weekday_index(text: str) -> Optional[int]:
    """
    The weekday number if the text is *just* a day heading, else None.

    Rejects ranges and sentences ("Wednesday - Saturday:", "served Monday to
    Friday"), which is what keeps opening hours out of the menu.
    """
    match = _PLAIN_WEEKDAY_PATTERN.match((text or "").strip())
    if not match:
        return None
    return WEEKDAY_INDEX_BY_NAME.get(match.group("name").lower())

class CurrentWeekday:
    def __init__(self, override_timezone=None, override_time=None):
        self.override_timezone: pytz.timezone = override_timezone
        self.override_time: datetime = override_time
        self.weekday: Weekdays = self.get_current_weekday()

    def get_current_weekday(self):
        timezone = self.override_timezone or pytz.timezone(TIMEZONE)
        current_time = self.override_time or datetime.now(timezone)

        return Weekdays(current_time.weekday())

    def as_swedish_str(self):
        return SWEDISH_NAMES[self.weekday.value]

    def as_english_str(self):
        return ENGLISH_NAMES[self.weekday.value]

    def iso_week(self) -> int:
        """The ISO week number of the current day."""
        timezone = self.override_timezone or pytz.timezone(TIMEZONE)
        current_time = self.override_time or datetime.now(timezone)
        return current_time.isocalendar()[1]

    def names(self):
        """Today's name in both languages, lowercase."""
        return [self.as_swedish_str().lower(), self.as_english_str().lower()]

    def matches(self, text: str) -> bool:
        """
        True if the text refers to today and to no other day.

        The "no other day" part matters: a heading like "Wednesday - Saturday"
        is opening hours, not Wednesday's lunch.
        """
        indices = weekday_indices_in(text)
        return bool(indices) and indices == {self.weekday.value}

    def __str__(self):
        return self.as_english_str()

    def __repr__(self):
        return f"CurrentWeekday(weekday={self.weekday}, timezone={self.override_timezone})"
