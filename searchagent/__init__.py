"""SearchAgent - AI-powered research assistant.

This package provides an AI researcher that can search the web, crawl pages,
build a knowledge base, and generate comprehensive research reports.
"""

__version__ = "2.0.0"

from .core import researcher, ChatManager
from .config import config, get_config

__all__ = [
    "researcher",
    "ChatManager",
    "config",
    "get_config",
]
