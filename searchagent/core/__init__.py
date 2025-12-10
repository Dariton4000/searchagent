"""Core functionality for SearchAgent.

This package contains the main research logic, chat management,
and orchestration components.
"""

from .chat_manager import ChatManager
from .researcher import researcher, get_tool_functions

__all__ = [
    "ChatManager",
    "researcher",
    "get_tool_functions",
]
