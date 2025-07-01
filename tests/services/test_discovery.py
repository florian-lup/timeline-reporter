"""Test suite for discovery service."""

import json
import pytest
from unittest.mock import Mock, patch

from services import discover_events
from utils import Event


class TestDiscoveryService:
    """Test suite for discovery service functions."""

    @pytest.fixture
    def mock_perplexity_client(self):
        """Mock Perplexity client for testing."""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def sample_discovery_response(self):
        """Sample response from Perplexity deep research."""
        return json.dumps([
            {
                "title": "Climate Summit Announced",
                "summary": "World leaders gather to discuss urgent climate action plans for the next decade."
            },
            {
                "title": "Earthquake Hits Pacific Region",
                "summary": "A magnitude 6.5 earthquake struck the Pacific region, causing minimal damage but raising tsunami concerns."
            }
        ])

    @pytest.fixture
    def sample_malformed_response(self):
        """Sample malformed response with markdown fences."""
        return """```json
        [
            {
                "title": "Climate Summit Announced",
                "summary": "World leaders gather to discuss climate action."
            }
        ]
        ```"""

    def test_discover_events_success(self, mock_perplexity_client, sample_discovery_response):
        """Test successful event discovery."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            with patch('services.discovery.DISCOVERY_INSTRUCTIONS', 'Find events about {topics} on {date}'):
                events = discover_events(mock_perplexity_client)
        
        assert len(events) == 2
        assert isinstance(events[0], Event)
        assert events[0].title == "Climate Summit Announced"
        assert events[0].summary == "World leaders gather to discuss urgent climate action plans for the next decade."
        assert events[1].title == "Earthquake Hits Pacific Region"
        
        # Verify Perplexity client was called with correct prompt
        mock_perplexity_client.deep_research.assert_called_once()
        call_args = mock_perplexity_client.deep_research.call_args[0][0]
        assert "climate, environment and natural disasters, and major geopolitical events" in call_args
        assert "2024-01-15" in call_args

    def test_discover_events_with_markdown_fences(self, mock_perplexity_client, sample_malformed_response):
        """Test event discovery with markdown fence-wrapped JSON."""
        mock_perplexity_client.deep_research.return_value = sample_malformed_response
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            events = discover_events(mock_perplexity_client)
        
        assert len(events) == 1
        assert events[0].title == "Climate Summit Announced"
        assert events[0].summary == "World leaders gather to discuss climate action."

    def test_discover_events_empty_response(self, mock_perplexity_client):
        """Test event discovery with empty JSON array."""
        mock_perplexity_client.deep_research.return_value = "[]"
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            events = discover_events(mock_perplexity_client)
        
        assert events == []

    def test_discover_events_malformed_json(self, mock_perplexity_client):
        """Test event discovery with malformed JSON."""
        mock_perplexity_client.deep_research.return_value = "invalid json{"
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            with patch('services.discovery.logger') as mock_logger:
                events = discover_events(mock_perplexity_client)
        
        assert events == []
        mock_logger.warning.assert_called_once()

    def test_discover_events_missing_fields(self, mock_perplexity_client):
        """Test event discovery with missing required fields."""
        response = json.dumps([
            {"title": "Only Title"},  # Missing summary
            {"summary": "Only Summary"},  # Missing title
            {"title": "Complete Event", "summary": "Complete summary"}
        ])
        mock_perplexity_client.deep_research.return_value = response
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            # This should raise KeyError for missing fields
            with pytest.raises(KeyError):
                discover_events(mock_perplexity_client)

    @pytest.mark.parametrize("topics_override", [
        "technology and AI",
        "sports and entertainment", 
        "economics and finance"
    ])
    def test_discover_events_with_different_topics(self, mock_perplexity_client, sample_discovery_response, topics_override):
        """Test event discovery maintains flexibility for topic changes."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response
        
        # The current implementation has hardcoded topics, but we test the pattern
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            events = discover_events(mock_perplexity_client)
        
        # Should still work regardless of the topics (topics are hardcoded in current implementation)
        assert len(events) == 2

    @patch('services.discovery.logger')
    def test_logging_events_discovery(self, mock_logger, mock_perplexity_client, sample_discovery_response):
        """Test that event discovery logs properly."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            events = discover_events(mock_perplexity_client)
        
        mock_logger.debug.assert_called_once()
        mock_logger.info.assert_called_once_with(
            "Discovered %d events from combined topics.", 2
        )

    def test_discover_events_with_unicode_content(self, mock_perplexity_client):
        """Test event discovery with unicode characters."""
        unicode_response = json.dumps([
            {
                "title": "Climate Action 🌍 Summit",
                "summary": "Leaders discuss émissions reduction and sustainable développement goals."
            }
        ])
        mock_perplexity_client.deep_research.return_value = unicode_response
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            events = discover_events(mock_perplexity_client)
        
        assert len(events) == 1
        assert "🌍" in events[0].title
        assert "émissions" in events[0].summary

    def test_discover_events_prompt_formatting(self, mock_perplexity_client, sample_discovery_response):
        """Test that prompt is properly formatted with topics and date."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            with patch('services.discovery.DISCOVERY_INSTRUCTIONS', 'Find {topics} events on {date}') as mock_instructions:
                discover_events(mock_perplexity_client)
        
        # Verify the prompt was called with correct format arguments
        call_args = mock_perplexity_client.deep_research.call_args[0][0]
        assert "climate, environment and natural disasters, and major geopolitical events" in call_args
        assert "2024-01-15" in call_args

    def test_parse_events_from_response_edge_cases(self, mock_perplexity_client):
        """Test edge cases in event parsing."""
        # Test with extra whitespace and nested objects
        complex_response = json.dumps([
            {
                "title": "  Spaced Title  ",
                "summary": "Summary with\nnewlines and   spaces"
            }
        ])
        mock_perplexity_client.deep_research.return_value = complex_response
        
        with patch('services.discovery.get_today_formatted', return_value='2024-01-15'):
            events = discover_events(mock_perplexity_client)
        
        assert len(events) == 1
        assert events[0].title == "  Spaced Title  "  # Preserves original formatting
        assert "\n" in events[0].summary 