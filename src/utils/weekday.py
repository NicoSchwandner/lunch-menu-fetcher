from datetime import datetime
import pytz
from config import TIMEZONE

def get_current_weekday():
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

    timezone = pytz.timezone(TIMEZONE)
    current_time = datetime.now(timezone)

    current_weekday_english = weekday_mapping_english[current_time.weekday()]
    current_weekday_swedish = weekday_mapping_swedish[current_time.weekday()]

    return current_weekday_english, current_weekday_swedish