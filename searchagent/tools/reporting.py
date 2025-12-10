"""Report generation for research findings.

This module provides functions to generate and save research reports
in markdown format.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List

import lmstudio as lms
from loguru import logger

from ..config import config


def sanitize_filename(title: str) -> str:
    """Sanitize a title for use as a filename.

    Removes or replaces characters that are invalid in filenames.

    Args:
        title: The title to sanitize

    Returns:
        Sanitized title safe for use as filename

    Raises:
        ValueError: If title is empty or contains only special characters
    """
    # Remove invalid characters, keep alphanumeric, spaces, hyphens
    sanitized = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')

    if not sanitized:
        raise ValueError("Report title cannot be empty or contain only special characters")

    return sanitized


def create_report(title: str, content: str, sources: List[str], chat=None) -> str:
    """Generate a final report in markdown format.

    This function creates a comprehensive research report and saves it
    to the reports directory. Only use this tool after all extensive
    research is completed.

    Args:
        title: The title of the report. Will be used for the filename
               combined with the current date and time.
        content: The extensive report content in markdown format.
        sources: A list of sources used in the report (URLs, citations, etc).
        chat: Optional chat object for token count calculation.

    Returns:
        Success message with the report file path, or an error message.

    Raises:
        ValueError: If title is invalid
        IOError: If report cannot be written to file

    Note:
        Saved reports cannot be changed or deleted. The filename includes
        a timestamp to ensure uniqueness.

    Example:
        >>> sources = ["https://example.com", "Wikipedia: AI"]
        >>> result = create_report(
        ...     "AI Research Summary",
        ...     "# Introduction\\n\\nAI is...",
        ...     sources
        ... )
        >>> print(result)
        DONE, Report saved to reports/AI_Research_Summary_20240101_120000.md
    """
    try:
        # Display token usage if chat is available
        if chat is not None:
            model = lms.llm()
            current_tokens = len(model.tokenize(str(chat)))
            context_length = model.get_context_length()
            remaining_percentage = round(
                ((context_length - current_tokens) / context_length) * 100
            )
            print(f"{current_tokens}/{context_length} ({remaining_percentage}%)")
            logger.info(
                f"Report creation - Token usage: {current_tokens}/{context_length} "
                f"({remaining_percentage}%)"
            )

        # Sanitize and validate title
        sanitized_title = sanitize_filename(title)
        logger.info(f"Creating report: {sanitized_title}")

        # Build report content
        report_content = f"# {sanitized_title}\n\n{content}\n\n## Sources\n"
        for source in sources:
            report_content += f"- {source}\n"

        # Ensure reports directory exists
        reports_dir = config.paths.reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Create unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f"{sanitized_title}_{timestamp}.md"

        # Write report to file
        with report_file.open("w", encoding="utf-8") as f:
            f.write(report_content)

        success_msg = f"DONE, Report saved to {report_file}"
        print(success_msg)
        logger.info(f"Report saved successfully: {report_file}")

        return success_msg

    except ValueError as e:
        error_message = f"Invalid report title: {e}"
        logger.error(error_message)
        print(error_message)
        return f"Error: {error_message}"

    except IOError as e:
        error_message = f"Error writing report to file: {e}"
        logger.error(error_message)
        print(error_message)
        return f"Error: {error_message}"

    except Exception as e:
        error_message = f"Unexpected error creating report: {e}"
        logger.error(error_message)
        print(error_message)
        return f"Error: {error_message}"
