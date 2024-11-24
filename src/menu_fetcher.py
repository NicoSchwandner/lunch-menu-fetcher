import logging

from src.restaurants.hildas import get_hildas_menu_data
from src.restaurants.bror_och_bord import get_bror_och_bord_menu_data
from src.restaurants.gabys import get_gabys_menu_data
from src.utils.weekday import get_current_weekday
from src.styling.menu_blocks import build_menu_blocks

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_menu_blocks():
    try:
        current_weekday_english, current_weekday_swedish = get_current_weekday()

        # List to hold menu data from all restaurants
        menu_data_list = []

        # Get menu data from Gaby's
        gabys_data, error = get_gabys_menu_data(current_weekday_english)
        if error:
            logger.error(f"Gaby's: {error}")
        else:
            menu_data_list.append(gabys_data)

        # Get menu data from Bror och Bord
        bror_och_bord_data, error = get_bror_och_bord_menu_data(current_weekday_swedish)
        if error:
            logger.error(f"Bror och Bord: {error}")
        else:
            menu_data_list.append(bror_och_bord_data)

        if not menu_data_list:
            return None, 'No menu data available.'

        # Get menu data from Hilda's
        hildas_data, error = get_hildas_menu_data(current_weekday_english)
        if error:
            logger.error(f"Hilda's: {error}")
        else:
            menu_data_list.append(hildas_data)

        # Build blocks for the Slack message
        blocks = build_menu_blocks(menu_data_list)

        return blocks, None

    except Exception as e:
        error_message = f"An error occurred while fetching the menu: {str(e)}"
        logger.error(error_message)
        return None, error_message
