import requests
from bs4 import BeautifulSoup
from config import BROR_OCH_BORD_MENU_URL, RESTAURANT_REQUEST_TIMEOUT
from utils.weekday import CurrentWeekday

def get_bror_och_bord_menu_data(current_weekday: CurrentWeekday):
    """
    Retrieves the menu data for Bror och Bord for the specified day of the week.

    Parameters:
        current_weekday (CurrentWeekday): An instance of CurrentWeekday.

    Returns:
        tuple: A tuple containing:
            - menu_data (dict): The extracted menu data.
            - error (str or None): An error message if extraction fails, else None.
    """
    try:
        response = requests.get(BROR_OCH_BORD_MENU_URL, timeout=RESTAURANT_REQUEST_TIMEOUT)
    except requests.RequestException as e:
        return None, f"Request failed: {e}"

    if response.status_code != 200:
        return None, f"Failed to retrieve menu. Status code: {response.status_code}"

    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the main container holding the menu
    # Adjust the selector based on the actual HTML structure
    menu_container = soup.find('div', class_='wpb_text_column')
    if not menu_container:
        return None, 'Menu container not found.'

    # Find all <p> tags within the menu container
    p_tags = menu_container.find_all('p')

    sections = []
    current_section = None

    for p in p_tags:
        strong = p.find('strong')
        if strong:
            # Found a section title (e.g., 'Måndag')
            section_title = strong.get_text(strip=True)
            # Initialize a new section
            current_section = {
                'heading': section_title,
                'items': []
            }
            sections.append(current_section)
        elif current_section:
            # Found menu items under the current section
            # Split the text by <br /> tags to get individual items
            # Since <br /> tags are converted to '\n' by BeautifulSoup's get_text with separator='\n'
            items_text = p.get_text(separator='\n', strip=True)
            items = [item.strip() for item in items_text.split('\n') if item.strip()]
            current_section['items'].extend(items)

    if not sections:
        return None, 'No menu sections found.'

    # Filter sections based on the current_weekday
    # Including 'Salad of the week' if applicable
    filtered_sections = [
        section for section in sections
        if current_weekday.as_swedish_str() in section['heading'] or 'Salad of the week' in section['heading']
    ]

    if not filtered_sections:
        return None, f"No menu found for {current_weekday}."

    menu_data = {
        'restaurant_name': "Bror och Bord",
        'sections': filtered_sections
    }

    return menu_data, None
