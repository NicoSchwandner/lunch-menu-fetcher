import logging
from typing import Dict, List, Optional, Tuple

from config import BROR_OCH_BORD_MENU_URL, RESTAURANT_REQUEST_TIMEOUT
from src.restaurants.general import extract_sections, get_website_content
from src.utils.weekday import CurrentWeekday


def extract_bror_och_bord_menu_sections(
    logger: logging.Logger,
    content: str
) -> Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
    """
    Extracts menu sections from the provided HTML content.

    Args:
        logger (logging.Logger): The logger instance.
        content (str): The HTML content of the website.

    Returns:
        Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
            A tuple containing:
            - A list of menu sections, where each section is a dict with 'heading' and 'items'.
            - An error message if extraction fails, otherwise None.
    """
    return extract_sections(logger, content)


def get_bror_och_bord_menu_data(
    logger: logging.Logger,
    current_weekday: CurrentWeekday
) -> Tuple[Optional[Dict[str, List[Dict[str, List[str]]]]], Optional[str]]:
    """
    Retrieves and filters the Bror och Bord menu data for the given weekday.

    Args:
        logger (logging.Logger): The logger instance.
        current_weekday (CurrentWeekday): An instance representing the current weekday.

    Returns:
        Tuple[Optional[Dict], Optional[str]]:
            - A dictionary containing restaurant name and relevant menu sections if successful.
            - An error message if data extraction fails.
    """
    content = get_website_content(logger, BROR_OCH_BORD_MENU_URL, RESTAURANT_REQUEST_TIMEOUT)
    if not content:
        return _log_and_return_error(logger, "Failed to retrieve website content.")

    sections, error = extract_bror_och_bord_menu_sections(logger, content)
    if error or sections is None:
        return None, error or "Failed to extract menu sections."

    filtered_sections = [
        section for section in sections
        if section['items'] and current_weekday.matches(section['heading'])
    ]

    if not filtered_sections:
        return _log_and_return_error(
            logger, f"No menu found for {current_weekday.as_swedish_str()}."
        )

    logger.info(f"Successfully extracted menu for {current_weekday} from Bror och Bord.")

    menu_data = {
        'restaurant_name': "Bror och Bord",
        'sections': filtered_sections
    }

    return menu_data, None


def _log_and_return_error(logger: logging.Logger, error_message: str) -> Tuple[None, str]:
    logger.error(error_message)
    return None, error_message
