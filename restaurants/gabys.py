import requests
from bs4 import BeautifulSoup
from config import GABYS_MENU_URL

def get_gabys_menu_text(current_weekday):
    response = requests.get(GABYS_MENU_URL)

    if response.status_code != 200:
        return 'Failed to retrieve menu.'

    soup = BeautifulSoup(response.content, 'html.parser')
    gabys_menu_div = soup.find('div', class_='gabys-menu')
    if not gabys_menu_div:
        return 'Menu not found.'

    # Find all <p> tags within the gabys_menu_div
    p_tags = gabys_menu_div.find_all('p')

    salad_text = ''
    day_menu_text = ''

    for p in p_tags:
        # Get the strong span text
        strong = p.find('strong')
        strong_span = strong.find('span') if strong else None
        if strong_span:
            section_title = strong_span.get_text(strip=True)

            # Check for "Salad of the week"
            if 'Salad of the week' in section_title:
                # Format the salad text with bullet points
                content = p.get_text(separator='\n', strip=True)
                lines = content.split('\n')
                # Skip the first line (section title)
                salad_lines = ['• ' + line for line in lines[1:]]
                salad_text = '\n'.join(salad_lines)

            # Check for current weekday
            elif current_weekday in section_title:
                # Format the day's menu with bullet points
                content = p.get_text(separator='\n', strip=True)
                lines = content.split('\n')
                # Skip the first line (day title)
                day_menu_lines = ['• ' + line for line in lines[1:]]
                day_menu_text = '\n'.join(day_menu_lines)

    if not salad_text:
        salad_text = 'Salad of the week not found.'
    if not day_menu_text:
        day_menu_text = f"{current_weekday}'s menu not found."

    # Combine the salad and day's menu with headers
    menu_text = f"*{current_weekday}:*\n{day_menu_text}\n\n*Salad of the week:*\n{salad_text}"
    return menu_text