import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

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

        # Dictionary to map futures to restaurant names
        future_to_restaurant = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Schedule the calls to fetch menu data
            future_to_restaurant[executor.submit(get_gabys_menu_data, current_weekday_english)] = "Gaby's"
            future_to_restaurant[executor.submit(get_bror_och_bord_menu_data, current_weekday_swedish)] = "Bror och Bord"
            future_to_restaurant[executor.submit(get_hildas_menu_data, current_weekday_english)] = "Hilda's"

            # Set an overall timeout for the fetching process
            timeout_seconds = 2.5

            for future in as_completed(future_to_restaurant, timeout=timeout_seconds):
                restaurant_name = future_to_restaurant[future]
                try:
                    menu_data, error = future.result()
                    if error:
                        logger.error(f"{restaurant_name}: {error}")
                    else:
                        menu_data_list.append(menu_data)
                except Exception as e:
                    logger.error(f"Exception occurred while fetching data for {restaurant_name}: {str(e)}")

        if not menu_data_list:
            return None, 'No menu data available.'

        # Build blocks for the Slack message
        blocks = build_menu_blocks(menu_data_list)

        return blocks, None

    except Exception as e:
        error_message = f"An error occurred while fetching the menu: {str(e)}"
        logger.error(error_message)
        return None, error_message
