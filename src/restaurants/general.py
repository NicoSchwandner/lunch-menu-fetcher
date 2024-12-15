import logging
from typing import Optional

import requests

def get_website_content(logger: logging.Logger, url: str, timeout: int) -> Optional[str]:
    """
    Retrieves the content of a website.

    Args:
        logger (logging.Logger): The logger instance.

    Returns:
        Optional[str]: The content of the website if successful, else None.
    """
    response = get_response(logger, url, timeout)

    return response.content

def get_json_data(logger: logging.Logger, url: str, timeout: int) -> Optional[dict]:
    """
    Retrieves JSON data from a URL.

    Args:
        logger (logging.Logger): The logger instance.

    Returns:
        Optional[dict]: The JSON data if successful, else None.
    """
    response = get_response(logger, url, timeout)

    try:
        return response.json()
    except ValueError:
        logger.error("Invalid JSON response.")
        return None

def get_response(logger: logging.Logger, url: str, timeout: int) -> Optional[requests.Response]:
    """
    Retrieves a response object from a URL.

    Args:
        logger (logging.Logger): The logger instance.

    Returns:
        Optional[requests.Response]: The response object if successful, else None.
    """
    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

    if response.status_code != 200:
        logger.error(f"Failed to retrieve website content. Status code: {response.status_code}")
        return None

    return response