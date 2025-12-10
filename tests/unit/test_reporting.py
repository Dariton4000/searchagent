"""Unit tests for reporting module."""

import pytest
from pathlib import Path

from searchagent.tools.reporting import sanitize_filename, create_report


class TestSanitizeFilename:
    """Test cases for filename sanitization."""

    def test_sanitize_normal_title(self):
        """Test sanitizing a normal title."""
        result = sanitize_filename("My Research Report")
        assert result == "My_Research_Report"

    def test_sanitize_special_characters(self):
        """Test removing special characters."""
        result = sanitize_filename("Report: AI & ML (2024)!")
        assert result == "Report_AI__ML_2024"

    def test_sanitize_empty_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            sanitize_filename("")

    def test_sanitize_only_special_chars_raises_error(self):
        """Test that title with only special chars raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            sanitize_filename("!@#$%^&*()")

    def test_sanitize_preserves_hyphens(self):
        """Test that hyphens are preserved."""
        result = sanitize_filename("AI-ML-Report")
        assert result == "AI-ML-Report"

    def test_sanitize_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        result = sanitize_filename("  My Report  ")
        assert result == "My_Report"


class TestCreateReport:
    """Test cases for report creation."""

    def test_create_report_success(self, temp_dir: Path, monkeypatch):
        """Test successful report creation."""
        monkeypatch.setattr("searchagent.tools.reporting.config.paths.reports_dir", temp_dir)

        result = create_report(
            title="Test Report",
            content="This is test content.",
            sources=["https://example.com", "Wikipedia: Test"],
            chat=None
        )

        assert "DONE" in result
        assert "Test_Report" in result

        # Check file was created
        report_files = list(temp_dir.glob("Test_Report_*.md"))
        assert len(report_files) == 1

        # Verify content
        content = report_files[0].read_text()
        assert "# Test_Report" in content
        assert "This is test content." in content
        assert "## Sources" in content
        assert "https://example.com" in content
        assert "Wikipedia: Test" in content

    def test_create_report_invalid_title(self, temp_dir: Path, monkeypatch):
        """Test report creation with invalid title."""
        monkeypatch.setattr("searchagent.tools.reporting.config.paths.reports_dir", temp_dir)

        result = create_report(
            title="!@#$%",
            content="Content",
            sources=[],
            chat=None
        )

        assert "Error" in result
        assert "Invalid report title" in result

    def test_create_report_with_sources(self, temp_dir: Path, monkeypatch):
        """Test report creation with multiple sources."""
        monkeypatch.setattr("searchagent.tools.reporting.config.paths.reports_dir", temp_dir)

        sources = [
            "https://example.com/article1",
            "https://example.com/article2",
            "Wikipedia: Machine Learning",
        ]

        result = create_report(
            title="ML Report",
            content="Machine learning content",
            sources=sources,
            chat=None
        )

        assert "DONE" in result

        # Verify sources in file
        report_files = list(temp_dir.glob("ML_Report_*.md"))
        content = report_files[0].read_text()

        for source in sources:
            assert source in content

    def test_create_report_unique_filenames(self, temp_dir: Path, monkeypatch):
        """Test that multiple reports get unique filenames."""
        import time
        monkeypatch.setattr("searchagent.tools.reporting.config.paths.reports_dir", temp_dir)

        # Create two reports with the same title
        create_report("Same Title", "Content 1", [], chat=None)
        time.sleep(1)  # Ensure different timestamps
        create_report("Same Title", "Content 2", [], chat=None)

        # Should have two different files
        report_files = list(temp_dir.glob("Same_Title_*.md"))
        assert len(report_files) == 2

        # Filenames should be different (different timestamps)
        assert report_files[0].name != report_files[1].name

    def test_create_report_creates_directory(self, temp_dir: Path, monkeypatch):
        """Test that reports directory is created if it doesn't exist."""
        reports_dir = temp_dir / "new_reports"
        monkeypatch.setattr("searchagent.tools.reporting.config.paths.reports_dir", reports_dir)

        assert not reports_dir.exists()

        create_report("Test", "Content", [], chat=None)

        assert reports_dir.exists()
        assert len(list(reports_dir.glob("*.md"))) == 1

    def test_create_report_with_mock_chat(self, temp_dir: Path, monkeypatch, mock_llm):
        """Test report creation with chat context for token counting."""
        monkeypatch.setattr("searchagent.tools.reporting.config.paths.reports_dir", temp_dir)

        mock_chat = "Some chat context"

        result = create_report(
            title="Report With Chat",
            content="Content",
            sources=[],
            chat=mock_chat
        )

        assert "DONE" in result
        # Should have called tokenize
        mock_llm.tokenize.assert_called()
