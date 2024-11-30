import json
from src.menu_fetcher import get_menu_blocks

def lambda_handler(event, context):
    blocks, error = get_menu_blocks()
    if error:
        response_text = error
        blocks = None
    else:
        response_text = "Here's today's menu:"

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'response_type': 'in_channel',
            'text': response_text,
            'blocks': blocks
        })
    }
