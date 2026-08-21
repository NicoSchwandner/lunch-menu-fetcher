from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import re
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
        {'name': "Gaby's",        'aliases': ('g', 'gabys'),  'function': get_gabys_menu_data},
        {'name': "Bror och Bord", 'aliases': ('b', 'bror'),   'function': get_bror_och_bord_menu_data},
        {'name': "Hilda's",       'aliases': ('h', 'hildas'), 'function': get_hildas_menu_data}
    ]


def filter_restaurants(restaurants: List[Dict[str, Callable]], query: str) -> List[Dict[str, Callable]]:
    """Pick the restaurant whose alias matches the query ("g"/"gabys", "b"/"bror", "h"/"hildas")."""
    query = re.sub(r'[^a-z0-9]', '', query.lower())
    if not query:
        return restaurants

    return [r for r in restaurants if query in r['aliases']]


def compile_and_post_menus(logger: logging.Logger, response_url: str, query: str = '') -> None:
    current_weekday = CurrentWeekday()
    restaurants = filter_restaurants(get_restaurants(), query)

    if not restaurants:
        logger.info(f"No restaurant matched '{query}'.")
        known = ", ".join(f"{r['name']} ({'/'.join(r['aliases'])})" for r in get_restaurants())
        send_slack_message(logger, response_url, SlackMessagePost(
            text=f'No restaurant matches "{query}". Try one of: {known}.',
            respone_type="ephemeral"
        ))
        return

    try:
        success_count = 0
        with ThreadPoolExecutor(max_workers=len(restaurants)) as executor:
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
