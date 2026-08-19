import logging
from typing import Dict, List, Optional, Tuple

from config import HILDAS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT
from src.restaurants.general import get_json_data
from src.utils.weekday import CurrentWeekday

def select_current_menu(logger: logging.Logger, data: List[Dict], current_weekday: CurrentWeekday) -> Dict:
    """
    Picks the menu for the current week, falling back to the newest one.

    The API returns one entry per week; matching on the week number means a late
    publish shows a stale menu with a warning instead of the wrong week silently.
    """
    current_week = current_weekday.iso_week()
    for entry in data:
        if str(entry.get('acf', {}).get('week', '')).strip() == str(current_week):
            return entry

    logger.warning(f"No menu published for week {current_week}; using the most recent one.")
    return data[0]

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
    latest_menu = select_current_menu(logger, data, current_weekday)
    days = latest_menu.get('acf', {}).get('days', [])

    if not days:
        return _log_and_return_error(logger, "No 'days' data found in the menu.")

    current_weekday_lower = current_weekday.as_english_str().lower()

    current_day_menu = next(
        (day for day in days if str(day.get('day', '')).strip().lower() == current_weekday_lower),
        None
    )
    if not current_day_menu:
        return _log_and_return_error(logger, f"No menu found for {current_weekday}.")

    category = str(current_day_menu.get('category') or '').strip()
    menu_items = current_day_menu.get('menu') or []

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
        title = str(item.get('title') or '').strip()
        text = ' '.join(str(item.get('text') or '').split())
        new_item = f"{title}: {text}" if title and text else title or text
        if new_item:
            formatted_items.append(new_item)

    return {
        'restaurant_name': "Hilda's",
        'sections': [
            {
                'heading': category or "Dagens lunch",
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
    logger.error(error_message)
    return None, error_message
