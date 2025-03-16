import logging
import re
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

    Adjusted to handle scenarios where a heading and its items 
    (like "Salad of the week") appear in the same <p>.

    Args:
        logger (logging.Logger): The logger instance.
        content (str): The HTML content of the website.
        current_weekday (CurrentWeekday): An instance representing the current weekday.

    Returns:
        Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
            - A list of menu sections, each containing a heading and items.
            - An error message if extraction fails, or None on success.
    """
    soup = BeautifulSoup(content, 'html.parser')

    # Attempt to find the new "weekly-menu" container.
    gabys_menu_div = soup.find('div', class_='weekly-menu')
    if not gabys_menu_div:
        # Fallback if there's still something else
        gabys_menu_div = soup.find('div', class_='gabys-menu')

    if not gabys_menu_div:
        return _log_and_return_error(logger, "Menu not found in markup.")

    # We will iterate over <p> tags and detect headings vs. items
    p_tags = gabys_menu_div.find_all('p')
    if not p_tags:
        return _log_and_return_error(logger, "No <p> tags found under weekly menu.")

    sections = []
    current_section = None
    current_weekday_str = current_weekday.as_english_str().lower()

    for p in p_tags:
        # Extract the full text of the paragraph, splitting on newline
        # to separate heading from additional text if they are in the same <p>.
        full_text = p.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]

        strong_tag = p.find('strong')
        span_in_strong = strong_tag.find('span') if strong_tag else None

        if span_in_strong:
            # We encountered a new heading in this paragraph
            if current_section:
                # Close off the previous section if it exists
                sections.append(current_section)

            # The first line is the heading; the rest (if any) are items in the same paragraph
            heading_line = lines[0]
            items = lines[1:]  # Remainder of lines in this paragraph are the items

            current_section = {
                'heading': heading_line,
                'items': items
            }
        else:
            # No heading => treat it as items for the current section, if there is one
            if current_section:
                current_section['items'].extend(lines)

    # Don't forget to append the last open section
    if current_section:
        sections.append(current_section)

    # Filter out only the sections that match the current weekday or "Salad of the week"
    filtered_sections = []
    for section in sections:
        heading_lower = section['heading'].lower()
        if current_weekday_str in heading_lower or "salad of the week" in heading_lower:
            filtered_sections.append(section)

    if not filtered_sections:
        return _log_and_return_error(
            logger, "No menu sections found matching current weekday or 'Salad of the week'."
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
