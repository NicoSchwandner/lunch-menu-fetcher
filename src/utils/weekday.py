from datetime import datetime
import pytz
from config import TIMEZONE

def get_current_weekday():
    # Define the mapping from weekday numbers to names
    weekday_mapping = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }

    timezone = pytz.timezone(TIMEZONE)
    current_time = datetime.now(timezone)
    current_weekday = weekday_mapping[current_time.weekday()]

    return current_weekday