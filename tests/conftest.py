"""Shared pytest fixtures and configuration.

This module provides common fixtures used across multiple test files.
"""

import json
import sys
from pathlib import Path
from typing import Generator
import tempfile
import shutil
from unittest.mock import MagicMock

import pytest

# Mock external modules before any imports
sys.modules['lmstudio'] = MagicMock()
sys.modules['crawl4ai'] = MagicMock()
sys.modules['ddgs'] = MagicMock()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing.

    Yields:
        Path to temporary directory

    Cleanup:
        Removes the directory after the test
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def knowledge_file(temp_dir: Path) -> Path:
    """Create a temporary knowledge file for testing.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path to temporary knowledge file
    """
    return temp_dir / "knowledge.json"


@pytest.fixture
def sample_knowledge_data() -> dict:
    """Provide sample knowledge data for testing.

    Returns:
        Dictionary with sample knowledge entries
    """
    return {
        "1": "Python is a high-level programming language.",
        "2": "Machine learning is a subset of artificial intelligence.",
        "3": "Neural networks are inspired by the human brain.",
    }


@pytest.fixture
def knowledge_file_with_data(knowledge_file: Path, sample_knowledge_data: dict) -> Path:
    """Create a knowledge file pre-populated with data.

    Args:
        knowledge_file: Path to knowledge file
        sample_knowledge_data: Sample data to populate

    Returns:
        Path to populated knowledge file
    """
    with knowledge_file.open("w") as f:
        json.dump(sample_knowledge_data, f)
    return knowledge_file


@pytest.fixture
def mock_llm(mocker):
    """Mock the LM Studio LLM for testing.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock LLM object
    """
    mock_model = mocker.MagicMock()
    mock_model.get_context_length.return_value = 32000
    mock_model.tokenize.return_value = [1] * 100  # 100 tokens
    mocker.patch("lmstudio.llm", return_value=mock_model)
    return mock_model


@pytest.fixture
def mock_chat(mocker):
    """Mock the LM Studio Chat for testing.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock Chat object
    """
    mock_chat_obj = mocker.MagicMock()
    mocker.patch("lmstudio.Chat", return_value=mock_chat_obj)
    return mock_chat_obj


@pytest.fixture
def sample_search_results() -> list:
    """Provide sample search results for testing.

    Returns:
        List of search result dictionaries
    """
    return [
        {
            "title": "Python Programming Language",
            "href": "https://www.python.org"
        },
        {
            "title": "Python Tutorial",
            "href": "https://docs.python.org/3/tutorial/"
        },
    ]


@pytest.fixture
def sample_wikipedia_response() -> dict:
    """Provide sample Wikipedia API response for testing.

    Returns:
        Dictionary simulating Wikipedia API response
    """
    return {
        "query": {
            "pages": {
                "12345": {
                    "title": "Python (programming language)",
                    "extract": "Python is a high-level, general-purpose programming language..."
                }
            }
        }
    }
