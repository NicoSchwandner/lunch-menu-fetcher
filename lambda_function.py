import json
from src.menu_fetcher import compile_and_post_menus
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def lambda_handler(event, context):
    """
    Secondary Lambda function to fetch lunch menu and respond to Slack.
    """
    response_url = event.get('response_url')

    # if not response_url:
    #     logger.error('Missing response_url in the event payload.')
    #     return {
    #         'statusCode': 400,
    #         'body': json.dumps({
    #             'message': 'Missing response_url.'
    #         })
    #     }

    try:
        compile_and_post_menus(logger, response_url)

    except Exception as e:
        logger.error(f'Error processing the request: {e}', exc_info=True)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Menu fetched successfully.'
        })
    }
