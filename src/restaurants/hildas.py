import logging
import requests
from config import HILDAS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT

from utils.weekday import CurrentWeekday

def get_hildas_menu_data(logger: logging.Logger, current_weekday: CurrentWeekday):
    """
    Retrieves the menu data for Hilda's for the specified day of the week.

    Parameters:
        current_weekday (CurrentWeekday): An instance of CurrentWeekday.

    Returns:
        tuple: A tuple containing:
            - menu_data (dict): The extracted menu data.
            - error (str or None): An error message if extraction fails, else None.
    """
    try:
        response = requests.get(HILDAS_MENU_URL, timeout=RESTAURANT_REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None, f"Request failed: {e}"

    try:
        data = response.json()
    except ValueError:
        logger.error("Invalid JSON response.")
        return None, "Invalid JSON response."

    if not isinstance(data, list):
        logger.error("Unexpected JSON structure. Expected a list.")
        return None, "Unexpected JSON structure."

    if not data:
        logger.error("No menu data found in the response.")
        return None, "No menu data found."

    # Assuming the latest menu is the first item in the list
    latest_menu = data[0]

    acf = latest_menu.get('acf', {})
    days = acf.get('days', [])

    if not days:
        logger.error("No 'days' data found in the menu.")
        return None, "No 'days' data found in the menu."

    # Normalize the current_weekday input
    current_weekday_lower = current_weekday.as_english_str().lower()

    if not current_weekday_lower:
        logger.error(f"Invalid or unsupported weekday: {current_weekday}")
        return None, f"Invalid or unsupported weekday: {current_weekday}"

    # Find the menu for the current weekday
    current_day_menu = next((day for day in days if day['day'].lower() == current_weekday_lower), None)

    if not current_day_menu:
        logger.error(f"No menu found for {current_weekday}.")
        return None, f"No menu found for {current_weekday}."

    category = current_day_menu.get('category', '').strip()
    menu_items = current_day_menu.get('menu', [])

    if not menu_items:
        logger.error(f"No menu items found for {current_weekday}.")
        return None, f"No menu items found for {current_weekday}."

    # Consolidate menu items into a list of strings
    # Format: "Title: Text"
    menu_items_text = []
    for item in menu_items:
        title = item.get('title', '').strip()
        text = item.get('text', '').strip().replace('\r\n', ' ').replace('\n', ' ')
        if title and text:
            combined_text = f"{title}: {text}"
        elif title:
            combined_text = title
        else:
            combined_text = text
        menu_items_text.append(combined_text)

    menu_data = {
        'restaurant_name': "Hilda's",
        'sections': [
            {
                'heading': category,
                'items': menu_items_text
            }
        ]
    }

    logger.info(f"Successfully extracted menu for {current_weekday} from Hilda's.")
    return menu_data, None
