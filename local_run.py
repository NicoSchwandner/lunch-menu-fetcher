import json
from freezegun import freeze_time
import responses
from lambda_function import lambda_handler
from config import GABYS_MENU_URL
from local.mock.gabys_html_mock import get_html_text

@responses.activate
def run_local():
    # Mock the request to Gaby's menu URL
    responses.add(
        responses.GET,
        GABYS_MENU_URL,
        body=get_html_text(),
        status=200,
        content_type='text/html'
    )

    # Use freezegun to set the current time to a specific day (e.g., Tuesday)
    with freeze_time("2024-11-26"):  # Assuming this date falls on a Tuesday
        # Simulate an event payload for AWS Lambda
        event = {}
        context = {}

        # Call the Lambda function handler
        response = lambda_handler(event, context)

        # Print the formatted response for easy debugging
        print(json.dumps(json.loads(response['body']), indent=2))

if __name__ == '__main__':
    run_local()