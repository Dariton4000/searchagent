"""Knowledge base management for research findings.

This module provides functions to store and retrieve research knowledge
in a persistent JSON-based knowledge base.
"""

import json
from pathlib import Path
from typing import List

from loguru import logger

from ..config import config


class KnowledgeBase:
    """Manages the research knowledge base with JSON storage.

    This class provides a simple key-value store for research findings,
    allowing the AI to build up knowledge incrementally and recall it later.

    Attributes:
        knowledge_file: Path to the JSON file storing knowledge
    """

    def __init__(self, knowledge_file: Path = None):
        """Initialize the knowledge base.

        Args:
            knowledge_file: Optional path to knowledge file. If None, uses
                           default from config.
        """
        if knowledge_file is None:
            knowledge_file = config.paths.knowledge_dir / config.knowledge.filename
        self.knowledge_file = knowledge_file

    def _load(self) -> dict:
        """Load knowledge from file.

        Returns:
            Dictionary of knowledge entries, or empty dict if file doesn't exist.
        """
        if not self.knowledge_file.exists():
            return {}

        try:
            with self.knowledge_file.open("r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode {self.knowledge_file}, starting fresh")
            return {}
        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")
            return {}

    def _save(self, data: dict) -> None:
        """Save knowledge to file.

        Args:
            data: Dictionary of knowledge entries to save
        """
        try:
            # Ensure directory exists
            self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)

            with self.knowledge_file.open("w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving knowledge: {e}")
            raise

    def save_knowledge(self, knowledge: str) -> str:
        """Add new knowledge to the knowledge base.

        Args:
            knowledge: The knowledge text to store

        Returns:
            Success message indicating the knowledge ID

        Raises:
            IOError: If the knowledge file cannot be written
        """
        # Load existing data
        data = self._load()

        # Determine next numeric key
        nums = [int(k) for k in data.keys() if k.isdigit()]
        next_num = max(nums, default=0) + 1

        # Add new knowledge
        data[str(next_num)] = knowledge

        # Save back to file
        self._save(data)

        logger.info(f"Knowledge {next_num} saved: {knowledge[:100]}...")
        print()
        print(f"Knowledge {next_num} saved: {knowledge}")

        return f"Knowledge {next_num} saved successfully."

    def get_all_knowledge(self) -> List[str]:
        """Retrieve all knowledge entries from the knowledge base.

        Returns:
            List of all knowledge entries in order of their numeric keys

        Note:
            Returns empty list if no knowledge exists.
        """
        print()
        print("Retrieving all knowledge entries")
        logger.info("Retrieving all knowledge entries")

        data = self._load()

        if not data:
            return []

        # Return entries sorted by numeric key
        try:
            return [data[key] for key in sorted(data.keys(), key=int)]
        except (ValueError, KeyError) as e:
            logger.warning(f"Error sorting knowledge entries: {e}")
            # Fallback to unsorted if keys aren't all numeric
            return list(data.values())


# Global knowledge base instance
_knowledge_base = None


def get_knowledge_base() -> KnowledgeBase:
    """Get the global knowledge base instance.

    Returns:
        The shared KnowledgeBase instance
    """
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base


# Tool functions for LLM
def save_knowledge(knowledge: str) -> str:
    """Add new knowledge for later use.

    This is the tool function exposed to the LLM for saving research findings.

    Args:
        knowledge: The knowledge text to store

    Returns:
        Success message indicating the knowledge ID
    """
    return get_knowledge_base().save_knowledge(knowledge)


def get_all_knowledge() -> List[str]:
    """Return all entries in the knowledge base.

    This is the tool function exposed to the LLM for retrieving saved knowledge.

    Returns:
        List of all knowledge entries
    """
    return get_knowledge_base().get_all_knowledge()
