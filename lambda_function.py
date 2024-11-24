import json
import threading
from urllib.parse import parse_qs
from src.menu_processor import process_menus, process_menus_and_respond
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        # Determine if we should process synchronously (for local testing)
        sync = event.get('sync', False)  # Default to False in production

        # Parse the request body
        body = event.get('body', '')
        params = parse_qs(body)
        response_url = params.get('response_url', [None])[0]

        if not response_url and not sync:
            logger.error("No response_url found in the request.")
            return {
                'statusCode': 400,
                'body': 'Bad Request: No response_url provided.'
            }

        # Immediate acknowledgment (only in production)
        if not sync:
            logger.info("Sending immediate acknowledgment to Slack.")
            acknowledgment_response = {
                'statusCode': 200,
                'body': ''
            }

            # Start a new thread to process the menus
            processing_thread = threading.Thread(target=process_menus_and_respond, args=(response_url,))
            processing_thread.start()

            return acknowledgment_response
        else:
            # Synchronous processing for local testing
            logger.info("Processing menus synchronously for local testing.")
            blocks, error = process_menus()
            if error:
                response_text = f"An error occurred: {error}"
                blocks = None
            else:
                response_text = "Here's today's menu:"

            # Prepare the Slack response
            slack_response = {
                'response_type': 'in_channel',
                'text': response_text,
                'blocks': blocks
            }

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(slack_response)
            }

    except Exception as e:
        logger.exception("An unexpected error occurred.")
        return {
            'statusCode': 500,
            'body': f"An unexpected error occurred: {str(e)}"
        }
