import logging
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from src.utils.weekday import ALL_WEEKDAY_NAMES, plain_weekday_index

# Browsers get served the menu; bare python-requests sometimes doesn't.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# Blocks that can hold a heading or a menu item. Deliberately narrow: enough to
# survive a restaurant swapping <p> for <li>, not so wide that we scrape nav menus.
BLOCK_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']
EMPHASIS_TAGS = ['strong', 'b', 'span', 'em', 'u', 'i']

# A heading is a short label ("Monday", "Salad of the week"), never a dish
# description, so anything long is an item no matter how it is marked up.
HEADING_MAX_LENGTH = 60


def get_website_content(logger: logging.Logger, url: str, timeout: float) -> Optional[str]:
    """Retrieves the raw content of a website, or None on failure."""
    response = get_response(logger, url, timeout)

    return response.content if response else None


def get_json_data(logger: logging.Logger, url: str, timeout: float) -> Optional[dict]:
    """Retrieves JSON data from a URL, or None on failure."""
    response = get_response(logger, url, timeout)
    if not response:
        return None

    try:
        return response.json()
    except ValueError:
        logger.error("Invalid JSON response.")
        return None


def get_response(logger: logging.Logger, url: str, timeout: float) -> Optional[requests.Response]:
    """Retrieves a response object from a URL, retrying once on failure."""
    for attempt in (1, 2):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={'User-Agent': USER_AGENT, 'Accept-Language': 'sv,en;q=0.8'},
            )
        except requests.RequestException as e:
            logger.warning(f"Request to {url} failed (attempt {attempt}): {e}")
            continue

        if response.status_code == 200:
            return response

        logger.warning(
            f"Request to {url} returned status {response.status_code} (attempt {attempt})."
        )

    logger.error(f"Failed to retrieve content from {url}.")
    return None


def normalize_text(text: str) -> str:
    """Collapses all whitespace, incl. non-breaking spaces, into single spaces."""
    return ' '.join((text or '').split())


def extract_sections(
    logger: logging.Logger,
    content: str,
    extra_headings: Tuple[str, ...] = (),
) -> Tuple[Optional[List[Dict[str, List[str]]]], Optional[str]]:
    """
    Extracts ``{'heading': ..., 'items': [...]}`` sections from a menu page.

    Headings are recognised by *text* (a weekday name in either language, or one
    of ``extra_headings``) and secondarily by *shape* (a short, fully emphasised
    block). Two independent signals means a restaurant restyling its markup -
    which has broken this scraper repeatedly - no longer takes the menu down.

    Args:
        logger: The logger instance.
        content: The HTML content of the page.
        extra_headings: Extra lowercase heading prefixes beyond the weekdays.

    Returns:
        A tuple of (sections, error message). Exactly one of the two is set.
    """
    keywords = tuple(ALL_WEEKDAY_NAMES) + tuple(h.lower() for h in extra_headings)
    soup = BeautifulSoup(content, 'html.parser')

    blocks = [b for b in soup.find_all(BLOCK_TAGS) if not b.find(BLOCK_TAGS)]
    named_headings = [b for b in blocks if _matches_keyword(_block_text(b), keywords)]

    if not named_headings:
        logger.error("No weekday headings found in the markup.")
        return None, "No weekday headings found in the markup."

    region = _menu_region(named_headings)
    region_blocks = [b for b in blocks if _is_within(b, region)]

    sections: List[Dict[str, List[str]]] = []
    for block in region_blocks:
        lines = [normalize_text(l) for l in block.get_text(separator='\n').split('\n')]
        lines = [l for l in lines if l]

        for line in lines:
            if _is_heading(line, keywords, block):
                sections.append({'heading': line, 'items': []})
            elif sections:
                sections[-1]['items'].append(line)

    if not sections:
        logger.error("No sections could be built from the menu markup.")
        return None, "No sections could be built from the menu markup."

    return sections, None


def _block_text(block) -> str:
    return normalize_text(block.get_text(separator=' '))


def _matches_keyword(text: str, keywords: Tuple[str, ...]) -> bool:
    lowered = text.lower()
    return bool(text) and len(text) <= HEADING_MAX_LENGTH and any(
        lowered.startswith(k) for k in keywords
    )


def _is_heading(line: str, keywords: Tuple[str, ...], block) -> bool:
    if _matches_keyword(line, keywords):
        return True
    if len(line) > HEADING_MAX_LENGTH:
        return False
    return _is_emphasized(block, line)


def _is_emphasized(block, line: str) -> bool:
    """True if the block is a real heading tag, or its text is wholly emphasised."""
    if block.name.startswith('h') and block.name[1:].isdigit():
        return True
    return any(
        normalize_text(tag.get_text(separator=' ')) == line
        for tag in block.find_all(EMPHASIS_TAGS)
    )


def _menu_region(headings):
    """
    The ancestor covering the most distinct weekdays - the weekly menu, whatever
    its class name. Only plain day headings count, so weekdays mentioned in the
    opening hours or the footer cannot widen the region to the whole page.
    Ties go to the deepest ancestor, keeping the region as tight as possible.
    """
    weekdays_per_ancestor = {}
    nodes = {}
    for heading in headings:
        weekday = plain_weekday_index(_block_text(heading))
        for parent in heading.parents:
            weekdays_per_ancestor.setdefault(id(parent), set()).add(weekday)
            nodes[id(parent)] = parent

    def score(key):
        days = weekdays_per_ancestor[key] - {None}
        return (len(days), len(list(nodes[key].parents)))

    return nodes[max(weekdays_per_ancestor, key=score)]


def _is_within(block, region) -> bool:
    return any(parent is region for parent in block.parents)
