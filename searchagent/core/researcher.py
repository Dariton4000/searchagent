"""Research orchestration for the AI researcher.

This module provides the main research workflow, coordinating between
the LLM, tools, and UI components.
"""

from typing import List, Callable

from loguru import logger

from .chat_manager import ChatManager
from ..ui import ProgressBarPrinter, FormattedPrinter
from ..tools import (
    duckduckgo_search,
    save_knowledge,
    get_all_knowledge,
    crawl4ai,
    create_report,
    get_wikipedia_page,
    context_details,
)


def _execute_research_round(chat_manager: ChatManager) -> None:
    """Execute a single research round with progress tracking.

    This helper function eliminates code duplication by centralizing
    the research round execution logic.

    Args:
        chat_manager: The chat manager instance to use
    """
    printer = FormattedPrinter()
    progress_printer = ProgressBarPrinter()

    print("Researcher: ", end="", flush=True)

    # Execute the research round with all callbacks
    chat_manager.execute_research_round(
        on_message=chat_manager.chat.append,
        on_prediction_fragment=printer.print_fragment,
        on_round_end=lambda round_index: context_details(chat_manager.chat),
        on_prompt_processing_progress=progress_printer.update_progress,
    )

    # Clear progress bar and finalize output
    progress_printer.clear()
    print("\rResearcher: ", end="", flush=True)
    printer.finalize()


def get_tool_functions() -> List[Callable]:
    """Get the list of tool functions available to the LLM.

    Returns:
        List of callable tool functions
    """
    return [
        duckduckgo_search,
        save_knowledge,
        get_all_knowledge,
        crawl4ai,
        create_report,
        get_wikipedia_page,
    ]


def researcher(query: str) -> None:
    """Run the AI researcher on the given query.

    This is the main entry point for research tasks. It initializes the
    chat session, executes the initial research, and then enters an
    interactive loop for follow-up questions.

    Args:
        query: The research query to investigate

    Example:
        >>> researcher("What are the latest developments in AI?")
        Researcher: [AI begins researching...]
        You (leave blank to exit): Tell me more about transformers
        Researcher: [AI provides additional information...]
        You (leave blank to exit):
        [Session ends]
    """
    logger.info(f"Starting research session for query: {query}")

    # Get tool functions
    tools = get_tool_functions()

    # Create chat manager
    chat_manager = ChatManager(query, tools)

    # Log initial context usage
    current, total, pct = chat_manager.get_context_usage()
    logger.info(f"Initial context usage: {current}/{total} ({pct}% remaining)")

    # Execute initial research
    _execute_research_round(chat_manager)

    # Enter interactive loop
    while True:
        try:
            user_input = input("You (leave blank to exit): ")
        except EOFError:
            print()
            break

        if not user_input:
            break

        # Add user message and execute another round
        chat_manager.add_user_message(user_input)

        # Log context usage
        current, total, pct = chat_manager.get_context_usage()
        logger.debug(f"Context usage: {current}/{total} ({pct}% remaining)")

        # Execute research round
        _execute_research_round(chat_manager)

    logger.info("Research session ended")
