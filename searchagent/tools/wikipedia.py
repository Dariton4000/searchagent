"""Wikipedia API integration for fetching encyclopedia content.

This module provides functions to fetch content from Wikipedia using
the official API, which is more efficient and compliant than crawling.
"""

import requests
import lmstudio as lms
from loguru import logger

from ..config import config


def get_wikipedia_page(page: str) -> str:
    """Get content from a Wikipedia page.

    This function fetches content from Wikipedia using the official API,
    which is more efficient and compliant than web crawling. If no exact
    match is found, it will return information about similar pages.

    Args:
        page: Exact title of the Wikipedia page to fetch.
              For example: "Python (programming language)"

    Returns:
        Page content as plain text, or an error message if the page
        cannot be found or fetched.

    Note:
        Use this instead of crawling Wikipedia pages directly. The
        Wikipedia API is faster, more reliable, and respects the
        Wikimedia Foundation's policies.

    Example:
        >>> content = get_wikipedia_page("Artificial intelligence")
        >>> print(content[:100])

    See Also:
        https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
    """
    print()
    print(f"Fetching Wikipedia page: {page}")
    logger.info(f"Wikipedia API request for page: {page}")

    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'explaintext': True,
        'titles': page
    }

    # Wikipedia API requires a descriptive User-Agent identifying the bot
    # See: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
    headers = {
        'User-Agent': config.search.user_agent
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=config.search.timeout
        )
        response.raise_for_status()

        data = response.json()
        pages = data.get('query', {}).get('pages', {})

        if not pages:
            result = "No page found."
            logger.warning(f"No Wikipedia page found for: {page}")
        else:
            page_data = next(iter(pages.values()))
            result = page_data.get('extract', "No content found for the given page.")

            if result == "No content found for the given page.":
                logger.warning(f"Wikipedia page exists but has no content: {page}")

    except requests.exceptions.Timeout:
        result = f"Error: Request timed out after {config.search.timeout} seconds"
        logger.error(f"Wikipedia API timeout for page: {page}")

    except requests.exceptions.RequestException as e:
        result = f"Error fetching Wikipedia page: {e}"
        logger.error(f"Wikipedia API error for page '{page}': {e}")

    except Exception as e:
        result = f"Unexpected error fetching Wikipedia page: {e}"
        logger.error(f"Unexpected error for Wikipedia page '{page}': {e}")

    # Log token count for monitoring
    try:
        model = lms.llm()
        token_count = len(model.tokenize(str(result)))
        print(f"Token count: {token_count}")
        logger.debug(f"Wikipedia content token count: {token_count}")
    except Exception as e:
        logger.warning(f"Could not calculate token count: {e}")

    return result
