import requests
from bs4 import BeautifulSoup
from config import GABYS_MENU_URL

def get_gabys_menu_data(current_weekday):
    response = requests.get(GABYS_MENU_URL)

    if response.status_code != 200:
        return None, 'Failed to retrieve menu.'

    soup = BeautifulSoup(response.content, 'html.parser')
    gabys_menu_div = soup.find('div', class_='gabys-menu')
    if not gabys_menu_div:
        return None, 'Menu not found.'

    # Find all <p> tags within the gabys_menu_div
    p_tags = gabys_menu_div.find_all('p')

    sections = []

    for p in p_tags:
        # Get the strong span text
        strong = p.find('strong')
        strong_span = strong.find('span') if strong else None
        if strong_span:
            section_title = strong_span.get_text(strip=True)

            # Get the content of the section
            content = p.get_text(separator='\n', strip=True)
            lines = content.split('\n')
            # Skip the first line (section title)
            items = lines[1:]

            # If it's the current weekday or "Salad of the week", add to sections
            if current_weekday in section_title or 'Salad of the week' in section_title:
                sections.append({
                    'heading': section_title,
                    'items': items
                })

    if not sections:
        return None, 'No menu sections found.'

    menu_data = {
        'restaurant_name': "Gaby's",
        'sections': sections
    }

    return menu_data, None
