"""Web crawling functionality using crawl4ai.

This module provides asynchronous web crawling capabilities to extract
content from web pages for research purposes.
"""

import asyncio
from urllib.parse import urlparse

import lmstudio as lms
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from loguru import logger

from ..config import config


def validate_url(url: str) -> bool:
    """Validate URL format and scheme.

    Args:
        url: The URL to validate

    Returns:
        True if URL is valid and uses http/https, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


async def crawl4ai_async(url: str) -> str:
    """Asynchronously crawl a URL and return its content.

    Args:
        url: The URL to crawl

    Returns:
        The page content in markdown format

    Raises:
        ValueError: If URL is invalid
        Exception: If crawling fails
    """
    if not validate_url(url):
        raise ValueError(f"Invalid URL format: {url}")

    browser_conf = BrowserConfig(headless=config.crawler.headless)
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS if config.crawler.bypass_cache else CacheMode.ENABLED
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_conf
        )
        # Return the markdown content
        return result.markdown  # type: ignore


def crawl4ai(url: str) -> str:
    """Crawl a given URL and return the text content.

    This function crawls a webpage after searching DuckDuckGo and returns
    the content in markdown format. It uses headless browser automation
    to handle JavaScript-heavy sites.

    Args:
        url: The URL to crawl. Must start with http:// or https://

    Returns:
        The text content of the page in markdown format

    Raises:
        ValueError: If URL format is invalid

    Note:
        Do not use this tool to crawl Wikipedia pages directly.
        Use get_wikipedia_page() instead for better performance
        and API compliance.

    Example:
        >>> content = crawl4ai("https://example.com/article")
        >>> print(content[:100])  # First 100 chars
    """
    print()
    print(f"Crawling {url}")
    logger.info(f"Crawling URL: {url}")

    try:
        # Validate URL before crawling
        if not validate_url(url):
            error_msg = f"Invalid URL format: {url}. URL must start with http:// or https://"
            logger.error(error_msg)
            return f"Error: {error_msg}"

        # Run async crawl
        result = asyncio.run(crawl4ai_async(url))

        # Log token count for monitoring
        model = lms.llm()
        token_count = len(model.tokenize(str(result)))
        print(f"Token count: {token_count}")
        logger.debug(f"Crawled content token count: {token_count}")

        return result

    except ValueError as e:
        # URL validation error
        error_msg = str(e)
        logger.error(error_msg)
        return f"Error: {error_msg}"

    except Exception as e:
        # Crawling error
        error_msg = f"Error crawling {url}: {e}"
        logger.error(error_msg)
        print(error_msg)
        return error_msg
