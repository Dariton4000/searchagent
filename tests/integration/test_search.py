"""Integration tests for search functionality."""

import json
import pytest
from unittest.mock import Mock, patch

from searchagent.tools.search import duckduckgo_search


class TestDuckDuckGoSearch:
    """Integration tests for DuckDuckGo search."""

    @pytest.mark.integration
    def test_search_returns_json(self):
        """Test that search returns valid JSON."""
        with patch('searchagent.tools.search.DDGS') as mock_ddgs:
            # Mock the search results
            mock_instance = Mock()
            mock_instance.text.return_value = [
                {'title': 'Test Result 1', 'href': 'https://example.com/1', 'body': 'Body 1'},
                {'title': 'Test Result 2', 'href': 'https://example.com/2', 'body': 'Body 2'},
            ]
            mock_ddgs.return_value = mock_instance

            result = duckduckgo_search("test query")

            # Should return valid JSON
            data = json.loads(result)
            assert isinstance(data, list)
            assert len(data) == 2

    @pytest.mark.integration
    def test_search_filters_fields(self):
        """Test that search only returns title and href."""
        with patch('searchagent.tools.search.DDGS') as mock_ddgs:
            mock_instance = Mock()
            mock_instance.text.return_value = [
                {
                    'title': 'Test',
                    'href': 'https://example.com',
                    'body': 'Should be filtered out',
                    'extra': 'Also filtered'
                },
            ]
            mock_ddgs.return_value = mock_instance

            result = duckduckgo_search("test")
            data = json.loads(result)

            assert len(data) == 1
            assert 'title' in data[0]
            assert 'href' in data[0]
            assert 'body' not in data[0]
            assert 'extra' not in data[0]

    @pytest.mark.integration
    def test_search_handles_error(self):
        """Test that search handles errors gracefully."""
        with patch('searchagent.tools.search.DDGS') as mock_ddgs:
            mock_instance = Mock()
            mock_instance.text.side_effect = Exception("Network error")
            mock_ddgs.return_value = mock_instance

            result = duckduckgo_search("test")

            # Should return empty JSON array on error
            data = json.loads(result)
            assert data == []

    @pytest.mark.integration
    def test_search_respects_max_results(self):
        """Test that search respects max_results config."""
        with patch('searchagent.tools.search.DDGS') as mock_ddgs:
            mock_instance = Mock()
            mock_instance.text.return_value = [
                {'title': f'Result {i}', 'href': f'https://example.com/{i}'}
                for i in range(10)
            ]
            mock_ddgs.return_value = mock_instance

            duckduckgo_search("test")

            # Should call with max_results from config
            from searchagent.config import config
            mock_instance.text.assert_called_with("test", max_results=config.search.max_results)
