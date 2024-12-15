from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import requests

from src.response.slack_response import SlackMessagePost
from src.restaurants.hildas import get_hildas_menu_data
from src.restaurants.bror_och_bord import get_bror_och_bord_menu_data
from src.restaurants.gabys import get_gabys_menu_data
from src.utils.weekday import CurrentWeekday
from src.styling.menu_blocks import build_menu_blocks

def send_slack_message(logger: logging.Logger, response_url: str, messagePost: SlackMessagePost) -> bool:
    response = requests.post(response_url, headers=messagePost.headers, data=messagePost.to_json())

    if response.status_code != 200:
        logger.error(f'Failed to send response to Slack: {response.status_code}, {response.text}')
        return False

    logger.info('Response sent to Slack successfully.')
    return True

def handle_completed_future(logger, future, future_to_restaurant, response_url) -> bool:
    restaurant = future_to_restaurant[future]
    try:
        menu_data, error = future.result()

        if error:
            logger.error(f"{restaurant['name']}: {error}")
            return False

        blocks = build_menu_blocks(logger, menu_data)

        messagePost = SlackMessagePost(blocks=blocks)
        return send_slack_message(logger, response_url, messagePost)

    except Exception as e:
        logger.error(f"Exception occurred while fetching data for {restaurant['name']}: {str(e)}")
        return False

def compile_and_post_menus(logger: logging.Logger, response_url: str):
    try:
        current_weekday = CurrentWeekday()

        # List of restaurants with their corresponding fetch functions and names
        restaurants = [
            {
                'name': "Gaby's",
                'function': get_gabys_menu_data
            },
            {
                'name': "Bror och Bord",
                'function': get_bror_och_bord_menu_data
            },
            {
                'name': "Hilda's",
                'function': get_hildas_menu_data
            }
        ]

        success_count = 0

        # Use ThreadPoolExecutor to fetch menus in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Create a mapping from future to restaurant info
            future_to_restaurant = {
                executor.submit(restaurant['function'], logger, current_weekday): restaurant
                for restaurant in restaurants
            }

            # As futures complete, collect results
            for future in as_completed(future_to_restaurant):
                success = handle_completed_future(logger, future, future_to_restaurant, response_url)
                success_count += 1 if success else 0

        if success_count == 0:
            logger.error("No menus were successfully fetched.")
            messagePost = SlackMessagePost(text="No menu was fetched successfully.", respone_type="ephemeral")
            send_slack_message(logger, response_url, messagePost)
            return

        logger.info(f"{success_count} menus were successfully fetched.")

    except Exception as e:
        logger.error(f"An error occurred while fetching the menu: {e}")
