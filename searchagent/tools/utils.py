"""Utility functions for SearchAgent tools.

This module provides helper functions used by various tools, such as
token counting and context management.
"""

import lmstudio as lms
from loguru import logger


def context_details(chat=None) -> None:
    """Display context window usage details.

    Shows current token usage, total context length, and remaining
    percentage. This helps monitor how much context is being used
    during research.

    Args:
        chat: Optional chat object to calculate tokens for. If None,
              only basic info is displayed.

    Example:
        >>> context_details(chat)
        5000/32000 (84%)
    """
    try:
        model = lms.llm()

        if chat is not None:
            token_count = len(model.tokenize(str(chat)))
            context_length = model.get_context_length()
            remaining_percentage = round(
                ((context_length - token_count) / context_length) * 100
            )

            output = f"{token_count}/{context_length} ({remaining_percentage}%)"
            print()
            print(output)
            print("\n")

            logger.debug(
                f"Context usage: {token_count}/{context_length} "
                f"({remaining_percentage}% remaining)"
            )
        else:
            # No chat provided, just show that we're tracking
            print()
            print("Context details unavailable (no chat provided)")
            print("\n")

    except Exception as e:
        logger.warning(f"Could not calculate context details: {e}")
        print()
        print("Context details unavailable")
        print("\n")
