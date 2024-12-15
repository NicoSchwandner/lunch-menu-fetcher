from datetime import datetime
from enum import Enum
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
        weekday_mapping_swedish = {
            0: 'Måndag',
            1: 'Tisdag',
            2: 'Onsdag',
            3: 'Torsdag',
            4: 'Fredag',
            5: 'Lördag',
            6: 'Söndag'
        }

        return weekday_mapping_swedish[self.weekday.value]

    def as_english_str(self):
        weekday_mapping_english = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }

        return weekday_mapping_english[self.weekday.value]

    def __str__(self):
        return self.as_english_str()

    def __repr__(self):
        return f"CurrentWeekday(weekday={self.weekday}, timezone={self.override_timezone})"