"""Chat session management for LLM interactions.

This module manages the chat session state, replacing the global chat
variable with proper encapsulation and dependency injection.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List, Callable

import lmstudio as lms
from loguru import logger

from ..config import config


class ChatManager:
    """Manages LLM chat sessions and tool interactions.

    This class encapsulates chat state and provides methods for managing
    the conversation with the LLM, including tool function registration
    and message handling.

    Attributes:
        chat: The LM Studio Chat instance
        model: The LLM model instance
        tools: List of tool functions available to the LLM
    """

    def __init__(self, query: str, tools: Optional[List[Callable]] = None):
        """Initialize a new chat session.

        Args:
            query: The research query to investigate
            tools: Optional list of tool functions to make available
        """
        self.model = lms.llm()
        self.tools = tools or []

        # Load system prompt template
        system_prompt = self._load_system_prompt(query)

        # Create chat instance
        self.chat = lms.Chat(system_prompt)

        # Add initial user message
        self.chat.add_user_message(f"Here is the research query given by the user: '{query}'")

        logger.info(f"Chat session initialized for query: {query}")

    def _load_system_prompt(self, query: str) -> str:
        """Load and format the system prompt template.

        Args:
            query: The research query to insert into the template

        Returns:
            Formatted system prompt string
        """
        template_path = Path(config.system_prompt_template)

        try:
            if template_path.exists():
                with template_path.open("r") as f:
                    template = f.read()
            else:
                # Fallback to inline template if file doesn't exist
                logger.warning(f"System prompt template not found at {template_path}, using default")
                template = self._get_default_template()

            # Format with timestamp and query
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return template.format(timestamp=now, query=query)

        except Exception as e:
            logger.error(f"Error loading system prompt template: {e}")
            # Fallback to default
            return self._get_default_template().format(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                query=query
            )

    def _get_default_template(self) -> str:
        """Get the default system prompt template.

        Returns:
            Default system prompt template string
        """
        return (
            "You are a task-focused AI researcher. The current date and time is {timestamp}. "
            "Begin researching immediately. Perform multiple online searches to gather reliable "
            "information. Crawl webpages for context. When possible use Wikipedia as a source. "
            "Research extensively, multiple searches and crawls, One Source is not enough. "
            "After crawling a webpage, store any useful knowledge in the research knowledge base, "
            "treat it like your permanent memory. Recall all stored knowledge before creating the "
            "final report. Don't forget to ground information in reliable sources, crawl pages "
            "after searching DuckDuckGo for this. Mark any assumptions clearly. Produce an extensive "
            "report in markdown format using the create_report tool, be sure to use this tool. "
            "Create the report ONLY when you are done with all research. Already saved reports can "
            "NOT be changed or deleted. Add some tables if you think it will help clarify the "
            "information. Here is the research query: '{query}'"
        )

    def add_user_message(self, message: str) -> None:
        """Add a user message to the chat.

        Args:
            message: The user's message text
        """
        self.chat.add_user_message(message)
        logger.debug(f"User message added: {message[:100]}...")

    def get_context_length(self) -> int:
        """Get the model's context length.

        Returns:
            Maximum context length in tokens
        """
        return self.model.get_context_length()

    def get_token_count(self) -> int:
        """Get the current token count for the chat.

        Returns:
            Number of tokens currently in the chat history
        """
        return len(self.model.tokenize(str(self.chat)))

    def get_context_usage(self) -> tuple[int, int, int]:
        """Get detailed context usage information.

        Returns:
            Tuple of (current_tokens, context_length, remaining_percentage)
        """
        current_tokens = self.get_token_count()
        context_length = self.get_context_length()
        remaining_percentage = round(
            ((context_length - current_tokens) / context_length) * 100
        )
        return current_tokens, context_length, remaining_percentage

    def execute_research_round(
        self,
        on_message: Optional[Callable] = None,
        on_prediction_fragment: Optional[Callable] = None,
        on_round_end: Optional[Callable] = None,
        on_prompt_processing_progress: Optional[Callable] = None,
    ) -> None:
        """Execute a single round of research with the LLM.

        Args:
            on_message: Callback for when a complete message is received
            on_prediction_fragment: Callback for streaming output fragments
            on_round_end: Callback for when the round ends
            on_prompt_processing_progress: Callback for progress updates
        """
        self.model.act(
            self.chat,
            self.tools,
            on_message=on_message or self.chat.append,
            on_prediction_fragment=on_prediction_fragment,
            on_round_end=on_round_end,
            on_prompt_processing_progress=on_prompt_processing_progress,
        )
