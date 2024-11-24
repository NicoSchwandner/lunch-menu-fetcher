from datetime import datetime
import pytz
from config import TIMEZONE

def get_current_weekday(weekday_language='english', weekday_index=None):

    if weekday_index is None:
        timezone = pytz.timezone(TIMEZONE)
        current_time = datetime.now(timezone)
        weekday_index = current_time.weekday()

    # Define the mapping from weekday numbers to names
    weekday_mapping_english = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }

    weekday_mapping_swedish = {
        0: 'Måndag',
        1: 'Tisdag',
        2: 'Onsdag',
        3: 'Torsdag',
        4: 'Fredag',
        5: 'Lördag',
        6: 'Söndag'
    }

    if weekday_language == 'english':
        current_weekday = weekday_mapping_english[weekday_index]
    elif weekday_language == 'swedish':
        current_weekday = weekday_mapping_swedish[weekday_index]
    else:
        raise ValueError("Invalid weekday language. Supported languages are 'english' and 'swedish'.")

    return current_weekday