import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import requests

from src.restaurants.hildas import get_hildas_menu_data
from src.restaurants.bror_och_bord import get_bror_och_bord_menu_data
from src.restaurants.gabys import get_gabys_menu_data
from src.utils.weekday import get_current_weekday
from src.styling.menu_blocks import build_menu_blocks

def compile_and_post_menus(logger: logging.Logger, response_url: str):
    try:
        # Get the current weekday in English and Swedish
        current_weekday_english, current_weekday_swedish = get_current_weekday()

        # List of restaurants with their corresponding fetch functions and names
        restaurants = [
            {
                'name': "Gaby's",
                'function': get_gabys_menu_data,
                'weekday': current_weekday_english
            },
            {
                'name': "Bror och Bord",
                'function': get_bror_och_bord_menu_data,
                'weekday': current_weekday_swedish
            },
            {
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

            # As futures complete, collect results
            for future in as_completed(future_to_restaurant):
                restaurant = future_to_restaurant[future]
                try:
                    menu_data, error = future.result()
                    if error:
                        logger.error(f"{restaurant['name']}: {error}")
                    else:
                        blocks = build_menu_blocks(menu_data)

                        headers = {'Content-Type': 'application/json'}
                        slack_payload = {
                            'response_type': 'in_channel',
                            'text': None,
                            'blocks': blocks
                        }
                        response = requests.post(response_url, headers=headers, data=json.dumps(slack_payload))

                        if response.status_code != 200:
                            logger.error(f'Failed to send response to Slack: {response.status_code}, {response.text}')
                        else:
                            logger.info('Response sent to Slack successfully.')
                except Exception as e:
                    logger.error(f"Exception occurred while fetching data for {restaurant['name']}: {str(e)}")

    except Exception as e:
        error_message = f"An error occurred while fetching the menu: {str(e)}"
        logger.error(error_message)
        return None, error_message
