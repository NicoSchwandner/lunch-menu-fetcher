from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import requests
from typing import List, Dict, Callable

from src.response.slack_response import SlackMessagePost
from src.restaurants.hildas import get_hildas_menu_data
from src.restaurants.bror_och_bord import get_bror_och_bord_menu_data
from src.restaurants.gabys import get_gabys_menu_data
from src.utils.weekday import CurrentWeekday
from src.styling.menu_blocks import build_menu_blocks

def send_slack_message(logger: logging.Logger, response_url: str, message_post: SlackMessagePost) -> bool:
    response = requests.post(
        response_url,
        headers=message_post.headers,
        data=message_post.to_json()
    )

    if response.status_code != 200:
        logger.error(f"Failed to send response to Slack: {response.status_code}, {response.text}")
        return False

    logger.info("Response sent to Slack successfully.")
    return True


def process_restaurant_result(
    logger: logging.Logger,
    future,
    restaurant: Dict[str, str],
    response_url: str
) -> bool:
    try:
        menu_data, error = future.result()

        if error:
            logger.error(f"{restaurant['name']}: {error}")
            return False

        blocks = build_menu_blocks(logger, menu_data)
        message_post = SlackMessagePost(blocks=blocks)
        return send_slack_message(logger, response_url, message_post)

    except Exception as e:
        logger.exception(f"Exception occurred while fetching data for {restaurant['name']}: {e}")
        return False


def get_restaurants() -> List[Dict[str, Callable]]:
    return [
        {'name': "Gaby's",        'function': get_gabys_menu_data},
        {'name': "Bror och Bord", 'function': get_bror_och_bord_menu_data},
        {'name': "Hilda's",       'function': get_hildas_menu_data}
    ]


def compile_and_post_menus(logger: logging.Logger, response_url: str) -> None:
    current_weekday = CurrentWeekday()
    restaurants = get_restaurants()

    try:
        success_count = 0
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_restaurant = {
                executor.submit(r['function'], logger, current_weekday): r
                for r in restaurants
            }

            for future in as_completed(future_to_restaurant):
                restaurant = future_to_restaurant[future]
                if process_restaurant_result(logger, future, restaurant, response_url):
                    success_count += 1

        if success_count == 0:
            logger.error("No menus were successfully fetched.")
            message_post = SlackMessagePost(
                text="No menu was fetched successfully.",
                respone_type="ephemeral"
            )
            send_slack_message(logger, response_url, message_post)
            return

        logger.info(f"{success_count} menus were successfully fetched.")

    except Exception as e:
        logger.exception(f"An error occurred while fetching the menu: {e}")
