import logging
from typing import Tuple, Optional, List, Dict

from config import HILDAS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT
from restaurants.general import get_json_data
from utils.weekday import CurrentWeekday

def extract_menu_items(
    logger: logging.Logger, data: List[Dict], current_weekday: CurrentWeekday
) -> Tuple[Optional[List[Dict[str, str]]], Optional[str]]:
    """
    Extracts menu items and category for the given weekday from the raw data.

    Args:
        logger (logging.Logger): The logger instance.
        data (List[Dict]): The raw menu data retrieved from the API.
        current_weekday (CurrentWeekday): The current weekday object.

    Returns:
        Tuple[Optional[List[Dict[str, str]]], Optional[str]]: A tuple containing:
            - The menu items as a list of dictionaries.
            - The category string, or an error message if extraction fails.
    """
    latest_menu = data[0]
    days = latest_menu.get('acf', {}).get('days', [])

    if not days:
        return _log_and_return_error(logger, "No 'days' data found in the menu.")

    current_weekday_lower = current_weekday.as_english_str().lower()

    if not current_weekday_lower:
        return _log_and_return_error(logger, f"Invalid or unsupported weekday: {current_weekday}")

    current_day_menu = next((day for day in days if day['day'].lower() == current_weekday_lower), None)
    if not current_day_menu:
        return _log_and_return_error(logger, f"No menu found for {current_weekday}.")

    category = current_day_menu.get('category', '').strip()
    menu_items = current_day_menu.get('menu', [])

    if not menu_items:
        return _log_and_return_error(logger, f"No menu items found for {current_weekday}.")

    return menu_items, category

def format_menu_data(menu_items: List[Dict[str, str]], category: str) -> Dict:
    """
    Formats menu data into a structured dictionary for output.

    Args:
        menu_items (List[Dict[str, str]]): The raw menu items to format.
        category (str): The category or heading for the menu.

    Returns:
        Dict: A formatted dictionary containing menu data.
    """
    formatted_items = []
    for item in menu_items:
        title = item.get('title', '').strip()
        text = item.get('text', '').strip().replace('\r\n', ' ').replace('\n', ' ')
        new_item = f"{title}: {text}" if title and text else title or text
        formatted_items.append(new_item)

    return {
        'restaurant_name': "Hilda's",
        'sections': [
            {
                'heading': category,
                'items': formatted_items,
            }
        ]
    }

def get_hildas_menu_data(
    logger: logging.Logger, current_weekday: CurrentWeekday
) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Retrieves the menu data for Hilda's for the specified day of the week.

    Args:
        logger (logging.Logger): The logger instance.
        current_weekday (CurrentWeekday): An instance of CurrentWeekday.

    Returns:
        Tuple[Optional[Dict], Optional[str]]: A tuple containing:
            - The extracted menu data as a dictionary.
            - An error message if extraction fails, or None on success.
    """
    data = get_json_data(logger, HILDAS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT)

    if data is None:
        return _log_and_return_error(logger, "Failed to retrieve menu data.")
    if not isinstance(data, list) or not data:
        return _log_and_return_error(logger, "Unexpected or empty JSON structure.")

    menu_items, category = extract_menu_items(logger, data, current_weekday)
    if menu_items is None:
        return None, category

    menu_data = format_menu_data(menu_items, category)

    logger.info(f"Successfully extracted menu for {current_weekday} from Hilda's.")
    return menu_data, None

def _log_and_return_error(logger: logging.Logger, error_message: str) -> Tuple[None, str]:
    """
    Logs an error message and returns it in a consistent format.

    Args:
        logger (logging.Logger): The logger instance.
        error_message (str): The error message to log.

    Returns:
        Tuple[None, str]: A tuple of None and the error message.
    """
    logger.error(error_message)
    return None, error_message
