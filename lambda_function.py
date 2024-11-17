import json
import requests
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    url = "https://jacyzhotel.com/en/restaurants/gabys/"
    response = requests.get(url)

    if response.status_code != 200:
        return {
            'statusCode': 200,
            'body': json.dumps({'text': 'Failed to retrieve menu.'})
        }

    soup = BeautifulSoup(response.content, 'html.parser')
    gabys_menu_div = soup.find('div', class_='gabys-menu')
    if not gabys_menu_div:
        return {
            'statusCode': 200,
            'body': json.dumps({'text': 'Menu not found.'})
        }

    menu_text = gabys_menu_div.get_text(separator='\n', strip=True)

    return {
        'statusCode': 200,
        'body': json.dumps({'text': menu_text})
    }
