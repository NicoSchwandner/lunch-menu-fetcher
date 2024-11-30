import json
import threading
from urllib.parse import parse_qs
import logging
import requests

from src.menu_fetcher import get_menu_blocks

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = event.get('body', '')
        params = parse_qs(body)
        response_url = params.get('response_url', [None])[0]
        user_id = params.get('user_id', [None])[0]
        channel_id = params.get('channel_id', [None])[0]

        logger.info(f"Received slash command from user_id: {user_id}, channel_id: {channel_id}")

        if not response_url:
            logger.error("No response_url found in the request.")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'response_type': 'ephemeral',
                    'text': 'Error: No response URL provided.'
                }),
                'headers': {'Content-Type': 'application/json'}
            }

        # Immediate response to Slack with "Fetching restaurant data..." ephemeral message
        loading_response = {
            'response_type': 'ephemeral',  # Message only visible to the user
            'text': "Fetching restaurant data..."
        }

        # Start asynchronous processing
        processing_thread = threading.Thread(target=process_menus_and_respond, args=(response_url,))
        processing_thread.start()

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(loading_response)
        }

    except Exception as e:
        logger.exception("An unexpected error occurred in lambda_handler.")
        error_response = {
            'response_type': 'ephemeral',
            'text': f"An unexpected error occurred: {str(e)}"
        }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(error_response)
        }

def process_menus_and_respond(response_url):
    try:
        logger.info("Starting asynchronous menu fetching.")

        blocks, error = get_menu_blocks()

        if error:
            response_text = f"An error occurred while fetching menus: {error}"
            blocks = None
        else:
            response_text = "Here's today's menu:"

        # If there was an error, send an ephemeral error message
        if error:
            slack_response = {
                'response_type': 'ephemeral',
                'text': response_text
            }
            send_slack_message(response_url, slack_response)
            return

        # If menus were fetched successfully, send separate messages per restaurant
        for menu_data in blocks:
            restaurant_name = menu_data.get('restaurant_name', 'Unknown Restaurant')
            sections = menu_data.get('sections', [])

            # Construct the message blocks for each restaurant
            restaurant_blocks = [
                {
                    'type': 'header',
                    'text': {
                        'type': 'plain_text',
                        'text': restaurant_name,
                        'emoji': True
                    }
                }
            ]

            for section in sections:
                heading = section.get('heading', '')
                items = section.get('items', [])

                # Add section heading
                restaurant_blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*{heading}*"
                    }
                })

                # Add each menu item
                for item in items:
                    restaurant_blocks.append({
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"- {item}"
                        }
                    })

            # Combine restaurant blocks into the message
            slack_response = {
                'response_type': 'in_channel',  # Visible to everyone in the channel
                'text': f"Menu for {restaurant_name}:",
                'blocks': restaurant_blocks
            }

            # Send the message to Slack
            send_slack_message(response_url, slack_response)

    except Exception as e:
        logger.exception("Failed to process menus and respond to Slack.")
        # Optionally, send an error message back to Slack
        error_response = {
            'response_type': 'ephemeral',
            'text': f"An error occurred while processing your request: {str(e)}"
        }
        send_slack_message(response_url, error_response)

def send_slack_message(response_url, payload):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(response_url, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send message to Slack: {response.status_code}, {response.text}")
        else:
            logger.info(f"Successfully sent message to Slack: {response.status_code}")
    except Exception as e:
        logger.exception(f"Exception occurred while sending message to Slack: {str(e)}")
