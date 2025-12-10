"""Constants used throughout the SearchAgent application.

This module centralizes all magic strings, ANSI color codes, and other
constant values to improve maintainability.
"""


class FormattingTags:
    """Tags used for parsing LLM reasoning content."""

    THINK_OPEN = "<think>"
    THINK_CLOSE = "</think>"
    CHANNEL_OPEN = "<|channel|>"
    MESSAGE_OPEN = "<|message|>"
    END_CLOSE = "<|end|>"


class ANSIColors:
    """ANSI color codes for terminal output."""

    # Basic colors
    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    # Control codes
    CLEAR_LINE = "\033[2K"


class ProgressSymbols:
    """Symbols used in progress bar display."""

    FILLED = "█"
    EMPTY = "░"
    LEFT_BRACKET = "▕"
    RIGHT_BRACKET = "▏"
