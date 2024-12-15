import logging
from bs4 import BeautifulSoup
from typing import Tuple, List, Dict, Optional

from config import BROR_OCH_BORD_MENU_URL, RESTAURANT_REQUEST_TIMEOUT
from restaurants.general import get_website_content
from utils.weekday import CurrentWeekday

def log_error_and_return_none(logger: logging.Logger, message: str) -> Tuple[None, str]:
    logger.error(message)
    return None, message

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
    soup = BeautifulSoup(content, 'html.parser')
    menu_container = soup.find('div', class_='wpb_text_column')

    if not menu_container:
        return log_error_and_return_none(logger, "Menu container not found.")

    p_tags = menu_container.find_all('p')
    sections = []
    current_section = None

    for p in p_tags:
        strong_tag = p.find('strong')
        if strong_tag:
            # This paragraph seems to represent a section heading
            section_title = strong_tag.get_text(strip=True)
            current_section = {
                'heading': section_title,
                'items': []
            }
            sections.append(current_section)
        elif current_section:
            # These paragraphs represent menu items under the current section
            items_text = p.get_text(separator='\n', strip=True)
            items = [item.strip() for item in items_text.split('\n') if item.strip()]
            current_section['items'].extend(items)

    if not sections:
        return log_error_and_return_none(logger, "No sections found in the menu.")

    return sections, None

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
        return log_error_and_return_none(logger, "Failed to retrieve website content.")

    sections, error = extract_bror_och_bord_menu_sections(logger, content)
    if error or sections is None:
        return None, error if error else "Failed to extract menu sections."

    # Filter sections to only those relevant to the current weekday or the "Salad of the week"
    weekday_str = current_weekday.as_swedish_str()
    filtered_sections = [
        section for section in sections
        if weekday_str in section['heading'] or 'Salad of the week' in section['heading']
    ]

    if not filtered_sections:
        return log_error_and_return_none(logger, f"No menu found for {weekday_str}.")

    menu_data = {
        'restaurant_name': "Bror och Bord",
        'sections': filtered_sections
    }

    return menu_data, None
