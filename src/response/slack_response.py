import json


class SlackMessagePost:
    """
    Class to generate a response for the Slack bot API to display a message in a channel.
    """

    def __init__(self, text: str = None, blocks: list = None, respone_type: str = 'in_channel', content_type: str = 'application/json'):
        self.text = text
        self.blocks = blocks
        self.response_type = respone_type
        self.content_type = content_type
        self.headers = {'Content-Type': self.content_type}

    def to_dict(self) -> dict:
        return {
            'response_type': self.response_type,
            'text': self.text,
            'blocks': self.blocks
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())