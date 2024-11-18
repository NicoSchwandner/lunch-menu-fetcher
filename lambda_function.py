import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def lambda_handler(event, context):
    # Define the mapping from weekday numbers to names
    weekday_mapping = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }

    # Specify the restaurant's timezone
    timezone = pytz.timezone('Europe/Stockholm')
    current_time = datetime.now(timezone)
    current_weekday = weekday_mapping[current_time.weekday()]

    url = "https://jacyzhotel.com/en/restaurants/gabys/"
    response = requests.get(url)

    if response.status_code != 200:
        menu_text = 'Failed to retrieve menu.'
    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        gabys_menu_div = soup.find('div', class_='gabys-menu')
        if not gabys_menu_div:
            menu_text = 'Menu not found.'
        else:
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

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'response_type': 'in_channel',
            'text': menu_text
        })
    }
