import logging

from src.restaurants.gabys import get_gabys_menu_data
from src.utils.weekday import get_current_weekday
from src.styling.menu_blocks import build_menu_blocks

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_menu_blocks():
    try:
        current_weekday = get_current_weekday()

        # List to hold menu data from all restaurants
        menu_data_list = []

        # Get menu data from Gaby's
        gabys_data, error = get_gabys_menu_data(current_weekday)
        if error:
            logger.error(f"Gaby's: {error}")
        else:
            menu_data_list.append(gabys_data)

        # Future: Add more restaurants here
        # Example:
        # another_restaurant_data, error = get_another_restaurant_data(current_weekday)
        # if error:
        #     logger.error(f"Another Restaurant: {error}")
        # else:
        #     menu_data_list.append(another_restaurant_data)

        if not menu_data_list:
            return None, 'No menu data available.'

        # Build blocks for the Slack message
        blocks = build_menu_blocks(menu_data_list)

        return blocks, None

    except Exception as e:
        error_message = f"An error occurred while fetching the menu: {str(e)}"
        logger.error(error_message)
        return None, error_message
