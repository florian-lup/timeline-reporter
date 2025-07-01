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

    @pytest.fixture
    def test_discovery_instructions(self):
        """Test-specific discovery instructions with fixed date."""
        return (
            "Identify significant news about climate, environment and natural disasters, and major geopolitical events from today 2024-01-15. "
            "Focus on major global developments, breaking news, and important updates that would be of interest to a general audience. "
            "Return your findings as a JSON array of events, where each event has 'title' and 'summary' fields. "
            "Example format: [{\"title\": \"Event Title\", \"summary\": \"Brief description...\"}]"
        )

    def test_discover_events_success(self, mock_perplexity_client, sample_discovery_response, test_discovery_instructions):
        """Test successful event discovery."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            events = discover_events(mock_perplexity_client)
        
        assert len(events) == 2
        assert isinstance(events[0], Event)
        assert events[0].title == "Climate Summit Announced"
        assert events[0].summary == "World leaders gather to discuss urgent climate action plans for the next decade."
        assert events[1].title == "Earthquake Hits Pacific Region"
        
        # Verify Perplexity client was called with correct prompt
        mock_perplexity_client.deep_research.assert_called_once_with(test_discovery_instructions)

    def test_discover_events_with_markdown_fences(self, mock_perplexity_client, sample_malformed_response, test_discovery_instructions):
        """Test event discovery with markdown fence-wrapped JSON."""
        mock_perplexity_client.deep_research.return_value = sample_malformed_response
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            events = discover_events(mock_perplexity_client)
        
        assert len(events) == 1
        assert events[0].title == "Climate Summit Announced"
        assert events[0].summary == "World leaders gather to discuss climate action."

    def test_discover_events_empty_response(self, mock_perplexity_client, test_discovery_instructions):
        """Test event discovery with empty JSON array."""
        mock_perplexity_client.deep_research.return_value = "[]"
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            events = discover_events(mock_perplexity_client)
        
        assert events == []

    def test_discover_events_malformed_json(self, mock_perplexity_client, test_discovery_instructions):
        """Test event discovery with malformed JSON."""
        mock_perplexity_client.deep_research.return_value = "invalid json{"
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            with patch('services.discovery.logger') as mock_logger:
                events = discover_events(mock_perplexity_client)
        
        assert events == []
        mock_logger.warning.assert_called()

    def test_discover_events_missing_fields(self, mock_perplexity_client, test_discovery_instructions):
        """Test event discovery with missing required fields."""
        response = json.dumps([
            {"title": "Only Title"},  # Missing summary
            {"summary": "Only Summary"},  # Missing title
            {"title": "Complete Event", "summary": "Complete summary"}
        ])
        mock_perplexity_client.deep_research.return_value = response
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
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
        
        # Create test instructions with different topics
        test_instructions = (
            f"Identify significant news about {topics_override} from today 2024-01-15. "
            "Focus on major global developments, breaking news, and important updates that would be of interest to a general audience. "
            "Return your findings as a JSON array of events, where each event has 'title' and 'summary' fields. "
            "Example format: [{\"title\": \"Event Title\", \"summary\": \"Brief description...\"}]"
        )
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_instructions):
            events = discover_events(mock_perplexity_client)
        
        # Should still work regardless of the topics
        assert len(events) == 2

    @patch('services.discovery.logger')
    def test_logging_events_discovery(self, mock_logger, mock_perplexity_client, sample_discovery_response, test_discovery_instructions):
        """Test that event discovery logs properly."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            events = discover_events(mock_perplexity_client)
        
        mock_logger.debug.assert_called_once()
        # Check that the specific log message was called
        mock_logger.info.assert_any_call(
            "Discovered %d events from combined topics.", 2
        )

    def test_discover_events_with_unicode_content(self, mock_perplexity_client, test_discovery_instructions):
        """Test event discovery with unicode characters."""
        unicode_response = json.dumps([
            {
                "title": "Climate Action 🌍 Summit",
                "summary": "Leaders discuss émissions reduction and sustainable développement goals."
            }
        ])
        mock_perplexity_client.deep_research.return_value = unicode_response
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            events = discover_events(mock_perplexity_client)
        
        assert len(events) == 1
        assert "🌍" in events[0].title
        assert "émissions" in events[0].summary

    def test_discover_events_prompt_formatting(self, mock_perplexity_client, sample_discovery_response, test_discovery_instructions):
        """Test that prompt is properly formatted with topics and date."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            discover_events(mock_perplexity_client)
        
        # Verify the prompt was called with correct content
        mock_perplexity_client.deep_research.assert_called_once_with(test_discovery_instructions)
        call_args = mock_perplexity_client.deep_research.call_args[0][0]
        assert "climate, environment and natural disasters, and major geopolitical events" in call_args
        assert "2024-01-15" in call_args

    def test_parse_events_from_response_edge_cases(self, mock_perplexity_client, test_discovery_instructions):
        """Test edge cases in event parsing."""
        # Test with extra whitespace and nested objects
        complex_response = json.dumps([
            {
                "title": "  Spaced Title  ",
                "summary": "Summary with\nnewlines and   spaces"
            }
        ])
        mock_perplexity_client.deep_research.return_value = complex_response
        
        with patch('services.discovery.DISCOVERY_INSTRUCTIONS', test_discovery_instructions):
            events = discover_events(mock_perplexity_client)
        
        assert len(events) == 1
        assert events[0].title == "  Spaced Title  "  # Preserves original formatting
        assert "\n" in events[0].summary 