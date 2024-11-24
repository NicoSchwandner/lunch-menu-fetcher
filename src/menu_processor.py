import json
import requests
import datetime
import pytz
import logging
from src.restaurants.gabys import get_gabys_menu_data
from src.restaurants.bror_och_bord import get_bror_och_bord_menu_data
from src.restaurants.hildas import get_hildas_menu_data
from src.styling.menu_blocks import build_menu_blocks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_menus():
    try:
        # Determine the current weekday in Swedish
        swedish_weekdays = [
            'Måndag', 'Tisdag', 'Onsdag', 'Torsdag',
            'Fredag', 'Lördag', 'Söndag'
        ]
        timezone = pytz.timezone('Europe/Stockholm')
        current_datetime = datetime.datetime.now(timezone)
        current_weekday_index = current_datetime.weekday()
        current_weekday = swedish_weekdays[current_weekday_index]

        logger.info(f"Current weekday: {current_weekday}")

        # Retrieve menus
        menus = []
        errors = []

        extractors = {
            "Gaby's": get_gabys_menu_data,
            "Bror och Bord": get_bror_och_bord_menu_data,
            "Hilda's": get_hildas_menu_data
        }

        for restaurant, extractor in extractors.items():
            menu, error = extractor(current_weekday_index)
            if error:
                logger.error(f"{restaurant}: {error}")
                errors.append(f"{restaurant}: {error}")
            else:
                menus.append(menu)

        if menus:
            blocks = build_menu_blocks(menus)
            return blocks, None
        else:
            return None, "No menu data available."

    except Exception as e:
        logger.exception("An error occurred while processing menus.")
        return None, str(e)

def process_menus_and_respond(response_url):
    logger.info("Starting asynchronous menu processing.")
    blocks, error = process_menus()
    if error:
        response_text = f"An error occurred: {error}"
        blocks = None
    else:
        response_text = "Here's today's menu:"

    slack_response = {
        'response_type': 'in_channel',
        'text': response_text,
        'blocks': blocks
    }

    # Send the response back to Slack
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(response_url, headers=headers, data=json.dumps(slack_response))
        logger.info(f"Slack response status: {response.status_code}")
        logger.info(f"Slack response text: {response.text}")
    except Exception as e:
        logger.exception("Failed to send response to Slack.")
