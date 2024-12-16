import json
from freezegun import freeze_time
import responses
from lambda_function import lambda_handler
from config import GABYS_MENU_URL, BROR_OCH_BORD_MENU_URL, HILDAS_MENU_URL
from local.mock.gabys_html_mock import get_html_text as get_gabys_html_text
from local.mock.bror_och_bord_html_mock import get_html_text as get_bror_och_bord_html_text
from local.mock.hildas_json_mock import get_json_text as get_hildas_json_text

@responses.activate
def run_local():
    # Mock the requests to the restaurant URLs
    responses.add(
        responses.GET,
        GABYS_MENU_URL,
        body=get_gabys_html_text(),
        status=200,
        content_type='text/html'
    )

    responses.add(
        responses.GET,
        BROR_OCH_BORD_MENU_URL,
        body=get_bror_och_bord_html_text(),
        status=200,
        content_type='text/html'
    )

    responses.add(
        responses.GET,
        HILDAS_MENU_URL,
        json=get_hildas_json_text(),
        status=200,
        content_type='application/json'
    )

    # Mock the Slack response URL
    slack_mock_url = "https://hooks.slack.com/services/TEST/WEBHOOK/URL"
    responses.add(
        responses.POST,
        slack_mock_url,
        json={"ok": True},
        status=200,
        content_type='application/json'
    )

    # Freeze time to ensure we get a consistent weekday
    with freeze_time("2024-11-26"):
        event = {
            "response_url": slack_mock_url
        }
        context = {}

        response = lambda_handler(event, context)
        print(json.dumps(response, indent=2))

    # After lambda_handler completes, inspect and write all requests to a text file
    with open('local/tmp/requests_output.txt', 'w') as f:
        for i, call in enumerate(responses.calls, start=1):
            f.write(f"Request {i}:\n")
            f.write(f"  URL: {call.request.url}\n")
            f.write(f"  Method: {call.request.method}\n")
            f.write(f"  Headers: {dict(call.request.headers)}\n")
            # Body may be bytes, so decode if necessary
            body = call.request.body.decode('utf-8') if hasattr(call.request.body, 'decode') else str(call.request.body)
            f.write(f"  Body: {body}\n\n")

if __name__ == '__main__':
    run_local()
