import logging

from restaurants.gabys import get_gabys_menu_text
from utils.weekday import get_current_weekday

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_menu_text():
    try:
        current_weekday = get_current_weekday()

        gabys_text = get_gabys_menu_text(current_weekday)
        menu_text = f"*Gaby's:*\n{gabys_text}"

        return menu_text
    except Exception as e:
        error_message = f"An error occurred while fetching the menu: {str(e)}"
        logger.error(error_message)
        return error_message
