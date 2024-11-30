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
        # Get the current weekday in English and Swedish
        current_weekday_english, current_weekday_swedish = get_current_weekday()

        # List of restaurants with their corresponding fetch functions and names, including order_index
        restaurants = [
            {
                'order_index': 1,
                'name': "Gaby's",
                'function': get_gabys_menu_data,
                'weekday': current_weekday_english
            },
            {
                'order_index': 2,
                'name': "Bror och Bord",
                'function': get_bror_och_bord_menu_data,
                'weekday': current_weekday_swedish
            },
            {
                'order_index': 3,
                'name': "Hilda's",
                'function': get_hildas_menu_data,
                'weekday': current_weekday_english
            }
        ]

        # Use ThreadPoolExecutor to fetch menus in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Create a mapping from future to restaurant info
            future_to_restaurant = {
                executor.submit(restaurant['function'], restaurant['weekday']): restaurant
                for restaurant in restaurants
            }

            # Set a timeout for the fetching process
            timeout_seconds = 2

            # List to hold menu data
            menu_data_list = []

            # As futures complete, collect results
            for future in as_completed(future_to_restaurant, timeout=timeout_seconds):
                restaurant = future_to_restaurant[future]
                try:
                    menu_data, error = future.result()
                    if error:
                        logger.error(f"{restaurant['name']}: {error}")
                    else:
                        # Attach order_index to menu_data for sorting later
                        menu_data['order_index'] = restaurant['order_index']
                        menu_data_list.append(menu_data)
                except Exception as e:
                    logger.error(f"Exception occurred while fetching data for {restaurant['name']}: {str(e)}")

        if not menu_data_list:
            return None, 'No menu data available.'

        # Sort the menu_data_list based on order_index
        menu_data_list.sort(key=lambda x: x['order_index'])

        # Build blocks for the Slack message
        blocks = build_menu_blocks(menu_data_list)

        return blocks, None

    except Exception as e:
        error_message = f"An error occurred while fetching the menu: {str(e)}"
        logger.error(error_message)
        return None, error_message
