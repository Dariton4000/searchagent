"""Output formatter for LLM responses.

This module handles streaming output from the LLM, including special formatting
for reasoning content (thinking tags) and analysis blocks.
"""

from typing import Any

from rich.console import Console
from rich.markdown import Markdown

from ..config import FormattingTags, ANSIColors


console = Console(force_terminal=True)


class FormattedPrinter:
    """Formats and prints LLM streaming output with special tag handling.

    This printer handles reasoning content from LLMs that use special tags
    like <think> for internal reasoning. It displays such content in a
    different style (greyed out) to distinguish it from the main response.

    The implementation is robust and handles edge cases like stray tags
    and interruptions during streaming.

    Attributes:
        current_buffer: Buffer for incoming fragments being processed
        bot_response_buffer: Accumulated response for final markdown rendering
        in_think_content_mode: Whether currently processing thinking tags
        in_analysis_mode: Whether currently processing analysis tags
    """

    def __init__(self):
        """Initialize the formatted printer."""
        self.current_buffer = ""
        self.bot_response_buffer = ""
        self.in_think_content_mode = False
        self.in_analysis_mode = False

    def print_fragment(self, fragment: Any, round_index: int = 0) -> None:
        """Process and print a fragment of LLM output.

        Args:
            fragment: Fragment object containing content to print
            round_index: Current round index (unused, for compatibility)
        """
        self.current_buffer += fragment.content
        self._process_buffer()

    def _process_buffer(self) -> None:
        """Process the current buffer, handling special tags.

        This method scans for special tags (<think>, <|channel|>, etc.) and
        applies appropriate formatting. It handles multiple tag types and
        ensures proper state transitions.
        """
        while self.current_buffer:
            if self.in_think_content_mode:
                self._process_think_mode()
            elif self.in_analysis_mode:
                self._process_analysis_mode()
            else:
                self._process_normal_mode()

    def _process_think_mode(self) -> None:
        """Process buffer content when in think mode (greyed out text)."""
        close_tag_index = self.current_buffer.find(FormattingTags.THINK_CLOSE)
        if close_tag_index != -1:
            # Found closing tag - print content and exit think mode
            text_to_print = self.current_buffer[:close_tag_index]
            print(text_to_print, end="", flush=True)
            print(ANSIColors.RESET, end="", flush=True)
            self.current_buffer = self.current_buffer[
                close_tag_index + len(FormattingTags.THINK_CLOSE) :
            ]
            self.in_think_content_mode = False
        else:
            # No closing tag yet - print everything and wait for more
            print(self.current_buffer, end="", flush=True)
            self.current_buffer = ""

    def _process_analysis_mode(self) -> None:
        """Process buffer content when in analysis mode (greyed out text)."""
        end_tag_index = self.current_buffer.find(FormattingTags.END_CLOSE)
        if end_tag_index != -1:
            # Found closing tag - print content and exit analysis mode
            text_to_print = self.current_buffer[:end_tag_index]
            print(text_to_print, end="", flush=True)
            print(ANSIColors.RESET, end="", flush=True)
            self.current_buffer = self.current_buffer[
                end_tag_index + len(FormattingTags.END_CLOSE) :
            ]
            self.in_analysis_mode = False
        else:
            # No closing tag yet - print everything and wait for more
            print(self.current_buffer, end="", flush=True)
            self.current_buffer = ""

    def _process_normal_mode(self) -> None:
        """Process buffer content in normal mode (looking for opening tags)."""
        think_open_tag_index = self.current_buffer.find(FormattingTags.THINK_OPEN)
        channel_open_tag_index = self.current_buffer.find(FormattingTags.CHANNEL_OPEN)

        # Determine which tag comes first
        first_tag_index = -1
        is_think_tag = False
        is_channel_tag = False

        if think_open_tag_index != -1 and (
            channel_open_tag_index == -1 or think_open_tag_index < channel_open_tag_index
        ):
            first_tag_index = think_open_tag_index
            is_think_tag = True
        elif channel_open_tag_index != -1:
            first_tag_index = channel_open_tag_index
            is_channel_tag = True

        if is_think_tag:
            self._handle_think_tag(first_tag_index)
        elif is_channel_tag:
            self._handle_channel_tag(first_tag_index)
        else:
            # No tags in buffer - accumulate response
            self.bot_response_buffer += self.current_buffer
            self.current_buffer = ""

    def _handle_think_tag(self, tag_index: int) -> None:
        """Handle <think> tag opening.

        Args:
            tag_index: Position of the opening tag in the buffer
        """
        # Save text before tag to response buffer
        text_to_print = self.current_buffer[:tag_index]
        self.bot_response_buffer += text_to_print

        # Enter think mode (greyed out)
        print(ANSIColors.GREY, end="", flush=True)
        self.current_buffer = self.current_buffer[
            tag_index + len(FormattingTags.THINK_OPEN) :
        ]
        self.in_think_content_mode = True

    def _handle_channel_tag(self, tag_index: int) -> None:
        """Handle <|channel|> tag opening.

        Args:
            tag_index: Position of the opening tag in the buffer
        """
        message_tag_index = self.current_buffer.find(FormattingTags.MESSAGE_OPEN)
        if message_tag_index != -1 and message_tag_index > tag_index:
            # Found complete channel...message sequence
            text_to_print = self.current_buffer[:tag_index]
            self.bot_response_buffer += text_to_print

            # Enter analysis mode (greyed out)
            print(ANSIColors.GREY, end="", flush=True)

            self.current_buffer = self.current_buffer[
                message_tag_index + len(FormattingTags.MESSAGE_OPEN) :
            ]
            self.in_analysis_mode = True
        else:
            # No message tag yet - accumulate and wait
            self.bot_response_buffer += self.current_buffer
            self.current_buffer = ""

    def finalize(self) -> None:
        """Finalize output and render accumulated markdown content.

        This method should be called when streaming is complete. It processes
        any remaining buffer content and renders the final markdown output.
        """
        self._process_buffer()

        # Reset any open formatting modes
        if self.in_think_content_mode or self.in_analysis_mode:
            print(ANSIColors.RESET, end="", flush=True)
            self.in_think_content_mode = False
            self.in_analysis_mode = False

        # Only print markdown if there's actual content (prevents empty blocks)
        if self.bot_response_buffer.strip():
            console.print(Markdown(self.bot_response_buffer))
        self.bot_response_buffer = ""
