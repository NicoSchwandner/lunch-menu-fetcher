import json

class LambdaResponse:
    """
    Class to generate a response for the primary Lambda function that triggers this secondary Lambda function.
    """

    def __init__(self, status_code: int = 200, message: str = "Hello from secondary Lambda function!"):
        self.status_code = status_code
        self.response_type = 'ephemeral'

    def to_dict(self) -> dict:
        return {
            'statusCode': self.status_code,
            'body': json.dumps({
                'message': self.message
            })
        }