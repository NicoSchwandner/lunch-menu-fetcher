import json
from menu_fetcher import get_menu_text

def lambda_handler(event, context):
    menu_text = get_menu_text()
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'response_type': 'in_channel',
            'text': menu_text
        })
    }
