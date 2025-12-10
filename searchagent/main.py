"""Main entry point for SearchAgent.

This module provides the command-line interface for the AI research assistant.
"""

from pathlib import Path

from loguru import logger

from .config import config
from .core import researcher
from .tools import get_knowledge_base


def setup_logging() -> None:
    """Configure logging for the application.

    Sets up file and console logging with appropriate levels and formatting.
    """
    # Ensure logs directory exists
    config.paths.logs_dir.mkdir(exist_ok=True)

    # Configure loguru
    logger.add(
        config.paths.logs_dir / "searchagent_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info("SearchAgent started")


def cleanup_knowledge_base() -> None:
    """Delete all existing knowledge files to start fresh.

    This is called at the start of each session to ensure a clean
    knowledge base for the new research task.
    """
    knowledge_dir = config.paths.knowledge_dir

    if not knowledge_dir.exists():
        return

    # Delete all JSON files in the knowledge directory
    deleted_count = 0
    for file in knowledge_dir.glob("*.json"):
        try:
            file.unlink()
            deleted_count += 1
        except Exception as e:
            logger.warning(f"Could not delete {file}: {e}")

    if deleted_count > 0:
        logger.info(f"Deleted {deleted_count} old knowledge file(s)")


def main() -> None:
    """Main entry point for the SearchAgent application.

    Initializes directories, sets up logging, gets user input for the
    research query, and starts the research process.
    """
    # Setup logging first
    setup_logging()

    # Ensure required directories exist (done by config __post_init__)
    logger.debug("Ensuring directories exist")

    # Clean up old knowledge files
    cleanup_knowledge_base()

    # Get research query from user
    research_topic = input("Please provide a research task for the ai researcher: ").strip()

    if not research_topic:
        print("No research task provided. Exiting.")
        logger.info("No research task provided, exiting")
        return

    logger.info(f"Research topic: {research_topic}")

    # Start the research
    try:
        researcher(research_topic)
    except KeyboardInterrupt:
        print("\n\nResearch interrupted by user.")
        logger.info("Research interrupted by user (KeyboardInterrupt)")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        logger.exception("Unexpected error during research")
        raise


if __name__ == "__main__":
    main()
