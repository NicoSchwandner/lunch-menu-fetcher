import logging
from typing import Dict, List, Optional, Tuple

from config import GABYS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT
from src.restaurants.general import extract_sections
from src.restaurants.general import get_website_content
from src.utils.weekday import CurrentWeekday

# Sections Gaby's lists once for the whole week, alongside the daily dishes.
GABYS_WEEKLY_HEADINGS = ('salad of the week', 'veckans sallad', 'green kitchen', 'poke bowl')

# Of those, the ones worth posting every day.
GABYS_ALWAYS_SHOWN = ('salad of the week', 'veckans sallad')


def extract_gabys_menu_sections(
    logger: logging.Logger, content: str, current_weekday: CurrentWeekday
) -> Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
    """
    Extracts today's menu sections from Gaby's website content.

    Args:
        logger (logging.Logger): The logger instance.
        content (str): The HTML content of the website.
        current_weekday (CurrentWeekday): An instance representing the current weekday.

    Returns:
        Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
            - A list of menu sections, each containing a heading and items.
            - An error message if extraction fails, or None on success.
    """
    sections, error = extract_sections(logger, content, extra_headings=GABYS_WEEKLY_HEADINGS)
    if error or sections is None:
        return None, error or "Failed to extract menu sections."

    filtered_sections = [
        section for section in sections
        if section['items'] and (
            current_weekday.matches(section['heading'])
            or _is_always_shown(section['heading'])
        )
    ]

    if not filtered_sections:
        return _log_and_return_error(
            logger, f"No menu found for {current_weekday.as_english_str()}."
        )

    return filtered_sections, None


def get_gabys_menu_data(
    logger: logging.Logger, current_weekday: CurrentWeekday
) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Retrieves the menu data for Gaby's for the specified day of the week.

    Args:
        logger (logging.Logger): The logger instance.
        current_weekday (CurrentWeekday): An instance of CurrentWeekday.

    Returns:
        Tuple[Optional[Dict], Optional[str]]:
            - The extracted menu data as a dictionary.
            - An error message if extraction fails, or None on success.
    """
    content = get_website_content(logger, GABYS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT)
    if not content:
        return _log_and_return_error(logger, "Failed to retrieve website content.")

    sections, error = extract_gabys_menu_sections(logger, content, current_weekday)
    if error:
        return None, error

    menu_data = {
        'restaurant_name': "Gaby's",
        'sections': sections
    }
    logger.info(f"Successfully extracted menu for {current_weekday.as_english_str()} from Gaby's.")
    return menu_data, None


def _is_always_shown(heading: str) -> bool:
    lowered = heading.lower()
    return any(name in lowered for name in GABYS_ALWAYS_SHOWN)


def _log_and_return_error(logger: logging.Logger, error_message: str) -> Tuple[None, str]:
    logger.error(error_message)
    return None, error_message
