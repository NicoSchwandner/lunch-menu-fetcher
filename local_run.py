import json
from lambda_function import lambda_handler

if __name__ == '__main__':
    # Simulate an event payload for AWS Lambda
    event = {
        # You can customize the event payload as needed to simulate Slack command inputs or other triggers
    }
    context = {}  # Lambda context, can be empty for local testing

    # Call the Lambda function handler
    response = lambda_handler(event, context)

    # Print the formatted response for easy debugging
    print(json.dumps(json.loads(response['body']), indent=2))
