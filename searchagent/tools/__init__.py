"""Tools package for SearchAgent.

This package contains all the tool functions that can be called by the
LLM during research, including web search, crawling, knowledge management,
and report generation.
"""

from .search import duckduckgo_search
from .crawler import crawl4ai
from .knowledge import save_knowledge, get_all_knowledge, get_knowledge_base
from .wikipedia import get_wikipedia_page
from .reporting import create_report
from .utils import context_details

__all__ = [
    "duckduckgo_search",
    "crawl4ai",
    "save_knowledge",
    "get_all_knowledge",
    "get_knowledge_base",
    "get_wikipedia_page",
    "create_report",
    "context_details",
]
