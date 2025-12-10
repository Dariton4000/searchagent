"""Web search functionality using DuckDuckGo.

This module provides search capabilities for finding relevant web pages
to support research tasks.
"""

import json
from typing import List, Dict

from ddgs import DDGS
from loguru import logger

from ..config import config


def duckduckgo_search(search_query: str) -> str:
    """Search DuckDuckGo for the given query and return results.

    This function performs a web search using DuckDuckGo and returns
    a list of results with titles and URLs that can be crawled for
    detailed information.

    Args:
        search_query: The query to search for. Treat it like a Google
                     search query - use natural language and keywords.

    Returns:
        JSON string containing search results with 'title' and 'href' fields.
        Returns empty JSON array on error.

    Example:
        >>> results = duckduckgo_search("python web scraping")
        >>> import json
        >>> parsed = json.loads(results)
        >>> for result in parsed:
        ...     print(result['title'], result['href'])

    Note:
        This function is designed to be called by the LLM as a tool.
        Results should be followed up with the crawl4ai tool to get
        full page content.
    """
    print()
    print(f"Searching DuckDuckGo for: {search_query}")
    logger.info(f"DuckDuckGo search: {search_query}")

    try:
        # Perform search with configured max results
        results = DDGS().text(
            search_query,
            max_results=config.search.max_results
        )

        # Filter to just title and href
        filtered_results = [
            {'title': r['title'], 'href': r['href']}
            for r in results
        ]

        logger.debug(f"Found {len(filtered_results)} results")
        print(filtered_results)

        return json.dumps(filtered_results)

    except Exception as e:
        logger.error(f"Error searching DuckDuckGo: {e}")
        print(f"Error searching DuckDuckGo: {e}")
        return json.dumps([])
