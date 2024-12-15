from src.response.lambda_response import LambdaResponse
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

    if not response_url:
        error_message = 'Missing response_url in the event payload.'
        logger.error(error_message)
        return LambdaResponse(status_code=400, message=error_message).to_dict()

    try:
        compile_and_post_menus(logger, response_url)

    except Exception as e:
        logger.error(f'Error processing the request: {e}', exc_info=True)
        return LambdaResponse(status_code=500, message=f'Error processing the request.\n\nInner exception: {e}').to_dict()

    return LambdaResponse(message='Menu fetched successfully.').to_dict()
