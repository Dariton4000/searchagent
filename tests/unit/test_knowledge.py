"""Unit tests for knowledge management module."""

import json
import pytest
from pathlib import Path

from searchagent.tools.knowledge import KnowledgeBase, save_knowledge, get_all_knowledge


class TestKnowledgeBase:
    """Test cases for the KnowledgeBase class."""

    def test_save_knowledge_creates_file(self, knowledge_file: Path):
        """Test that saving knowledge creates the file."""
        kb = KnowledgeBase(knowledge_file)
        result = kb.save_knowledge("Test knowledge entry")

        assert knowledge_file.exists()
        assert "Knowledge 1 saved successfully" in result

    def test_save_knowledge_increments_id(self, knowledge_file: Path):
        """Test that knowledge IDs increment correctly."""
        kb = KnowledgeBase(knowledge_file)

        kb.save_knowledge("First entry")
        result = kb.save_knowledge("Second entry")

        assert "Knowledge 2 saved successfully" in result

        # Verify the data
        with knowledge_file.open("r") as f:
            data = json.load(f)
        assert "1" in data
        assert "2" in data
        assert data["1"] == "First entry"
        assert data["2"] == "Second entry"

    def test_get_all_knowledge_empty(self, knowledge_file: Path):
        """Test getting knowledge when file doesn't exist."""
        kb = KnowledgeBase(knowledge_file)
        result = kb.get_all_knowledge()

        assert result == []

    def test_get_all_knowledge_with_data(
        self, knowledge_file_with_data: Path, sample_knowledge_data: dict
    ):
        """Test retrieving all knowledge entries."""
        kb = KnowledgeBase(knowledge_file_with_data)
        result = kb.get_all_knowledge()

        assert len(result) == 3
        assert result[0] == sample_knowledge_data["1"]
        assert result[1] == sample_knowledge_data["2"]
        assert result[2] == sample_knowledge_data["3"]

    def test_get_all_knowledge_sorted_order(self, knowledge_file: Path):
        """Test that knowledge entries are returned in sorted order."""
        kb = KnowledgeBase(knowledge_file)

        # Add entries in non-sequential order
        kb.save_knowledge("First")
        kb.save_knowledge("Second")
        kb.save_knowledge("Third")

        result = kb.get_all_knowledge()

        assert result == ["First", "Second", "Third"]

    def test_load_corrupted_json(self, knowledge_file: Path):
        """Test handling of corrupted JSON file."""
        # Create a corrupted JSON file
        with knowledge_file.open("w") as f:
            f.write("{ invalid json }")

        kb = KnowledgeBase(knowledge_file)
        result = kb.get_all_knowledge()

        # Should return empty list and not crash
        assert result == []

    def test_save_after_corrupted_json(self, knowledge_file: Path):
        """Test that saving works after encountering corrupted JSON."""
        # Create a corrupted JSON file
        with knowledge_file.open("w") as f:
            f.write("{ invalid json }")

        kb = KnowledgeBase(knowledge_file)
        result = kb.save_knowledge("New entry")

        assert "Knowledge 1 saved successfully" in result

        # Verify it created valid JSON
        with knowledge_file.open("r") as f:
            data = json.load(f)
        assert data == {"1": "New entry"}


class TestKnowledgeFunctions:
    """Test the module-level functions."""

    def test_save_knowledge_function(self, temp_dir: Path, monkeypatch):
        """Test the save_knowledge function."""
        from searchagent.tools import knowledge as kb_module

        # Override the knowledge directory
        monkeypatch.setattr("searchagent.tools.knowledge.config.paths.knowledge_dir", temp_dir)
        monkeypatch.setattr("searchagent.tools.knowledge.config.knowledge.filename", "test_knowledge.json")

        # Reset the global instance
        kb_module._knowledge_base = None

        result = save_knowledge("Test entry")

        assert "Knowledge 1 saved successfully" in result
        assert (temp_dir / "test_knowledge.json").exists()

    def test_get_all_knowledge_function(self, temp_dir: Path, monkeypatch):
        """Test the get_all_knowledge function."""
        from searchagent.tools import knowledge as kb_module

        # Setup
        monkeypatch.setattr("searchagent.tools.knowledge.config.paths.knowledge_dir", temp_dir)
        monkeypatch.setattr("searchagent.tools.knowledge.config.knowledge.filename", "test_knowledge.json")
        kb_module._knowledge_base = None

        # Add some knowledge
        save_knowledge("Entry 1")
        save_knowledge("Entry 2")

        # Retrieve
        result = get_all_knowledge()

        assert len(result) == 2
        assert result[0] == "Entry 1"
        assert result[1] == "Entry 2"
