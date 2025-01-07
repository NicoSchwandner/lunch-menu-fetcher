import logging
from typing import Tuple, Optional, Dict, List
from bs4 import BeautifulSoup
from config import GABYS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT
from src.restaurants.general import get_website_content
from src.utils.weekday import CurrentWeekday


def extract_gabys_menu_sections(
    logger: logging.Logger, content: str, current_weekday: CurrentWeekday
) -> Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
    """
    Extracts menu sections from Gaby's website content for the given weekday.

    Args:
        logger (logging.Logger): The logger instance.
        content (str): The HTML content of the website.
        current_weekday (CurrentWeekday): An instance representing the current weekday.

    Returns:
        Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
            - A list of menu sections, each containing a heading and items.
            - An error message if extraction fails, or None on success.
    """
    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    gabys_menu_div = soup.find('div', class_='gabys-menu')
    if not gabys_menu_div:
        gabys_menu_div = soup.find('div', class_='weekly-menu')

    if not gabys_menu_div:
        return _log_and_return_error(logger, "Menu not found.")

    sections = []
    current_weekday_str = current_weekday.as_english_str()

    for p in gabys_menu_div.find_all('p'):
        # Extract section title
        strong = p.find('strong')
        strong_span = strong.find('span') if strong else None
        section_title = strong_span.get_text(strip=True) if strong_span else None

        if not section_title:
            continue

        # Extract menu items within the section
        content = p.get_text(separator='\n', strip=True)
        lines = content.split('\n')
        items = lines[1:]  # Skip the first line, as it is the section title

        # Filter by current weekday or "Salad of the week"
        if current_weekday_str in section_title or "Salad of the week" in section_title:
            sections.append({
                'heading': section_title,
                'items': items
            })

    if not sections:
        return _log_and_return_error(logger, "No menu sections found.")

    return sections, None


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
    # Fetch the raw website content
    content = get_website_content(logger, GABYS_MENU_URL, RESTAURANT_REQUEST_TIMEOUT)
    if not content:
        return _log_and_return_error(logger, "Failed to retrieve website content.")

    # Extract menu sections
    sections, error = extract_gabys_menu_sections(logger, content, current_weekday)
    if error:
        return None, error

    # Format the menu data
    menu_data = {
        'restaurant_name': "Gaby's",
        'sections': sections
    }

    logger.info(f"Successfully extracted menu for {current_weekday} from Gaby's.")
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
