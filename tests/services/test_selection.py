"""Test suite for decision service."""

from unittest.mock import Mock, patch

import pytest

from services import curate_leads
from models import Lead


class TestDecisionService:
    """Test suite for decision service functions."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        return Mock()

    @pytest.fixture
    def sample_events(self):
        """Sample events for testing."""
        return [
            Lead(
                context="Climate Summit 2024: World leaders meet to discuss climate change solutions and carbon reduction targets.",
            ),
            Lead(
                context="Earthquake in Pacific: A 6.5 magnitude earthquake struck the Pacific region with minimal damage reported.",
            ),
            Lead(
                context="Tech Conference Announced: Major technology companies announce new AI developments at annual conference.",
            ),
            Lead(
                context="Economic Policy Update: Government announces new economic policies affecting global markets.",
            ),
            Lead(
                context="Space Mission Success: NASA successfully launches new Mars exploration mission.",
            ),
        ]

    @pytest.fixture
    def sample_ai_response(self):
        """Sample AI response selecting events."""
        return "1, 3, 5"  # Select events 1, 3, and 5

    def test_curate_leads_basic(self, mock_openai_client, sample_events, sample_ai_response):
        """Test basic functionality of curate_leads."""
        mock_openai_client.chat_completion.return_value = sample_ai_response

        result = curate_leads(sample_events, openai_client=mock_openai_client)

        assert len(result) == 3
        assert result[0] == sample_events[0]  # Index 1 -> 0
        assert result[1] == sample_events[2]  # Index 3 -> 2
        assert result[2] == sample_events[4]  # Index 5 -> 4

    def test_curate_leads_empty_input(self, mock_openai_client):
        """Test curate_leads with empty input."""
        result = curate_leads([], openai_client=mock_openai_client)
        
        assert result == []
        mock_openai_client.chat_completion.assert_not_called()

    def test_curate_leads_no_valid_numbers(self, mock_openai_client, sample_events):
        """Test when AI response contains no valid numbers."""
        mock_openai_client.chat_completion.return_value = "No events selected"
        
        result = curate_leads(sample_events, openai_client=mock_openai_client)
        
        # Should return first 3 events as fallback
        assert len(result) == 3
        assert result == sample_events[:3]

    def test_curate_leads_invalid_indices(self, mock_openai_client, sample_events):
        """Test when AI response contains invalid indices."""
        mock_openai_client.chat_completion.return_value = "1, 10, 15"  # Indices 10 and 15 are out of range
        
        result = curate_leads(sample_events, openai_client=mock_openai_client)
        
        # Should only include valid index (1)
        assert len(result) == 1
        assert result[0] == sample_events[0]

    def test_curate_leads_mixed_valid_invalid(self, mock_openai_client, sample_events):
        """Test when AI response has mix of valid and invalid indices."""
        mock_openai_client.chat_completion.return_value = "1, 3, 10, 2"  # Index 10 is invalid
        
        result = curate_leads(sample_events, openai_client=mock_openai_client)
        
        # Should include only valid indices (1, 3, 2)
        assert len(result) == 3
        assert result[0] == sample_events[0]  # Index 1
        assert result[1] == sample_events[2]  # Index 3  
        assert result[2] == sample_events[1]  # Index 2

    def test_curate_leads_formats_events_correctly(self, mock_openai_client, sample_events):
        """Test that events are formatted correctly for AI evaluation."""
        mock_openai_client.chat_completion.return_value = "1"
        
        curate_leads(sample_events, openai_client=mock_openai_client)
        
        # Verify the prompt formatting
        call_args = mock_openai_client.chat_completion.call_args[0][0]
        
        # Should contain numbered events with context
        assert "1. Climate Summit 2024: World leaders meet to discuss climate change solutions and carbon reduction targets." in call_args
        assert "2. Earthquake in Pacific: A 6.5 magnitude earthquake struck the Pacific region with minimal damage reported." in call_args

    @patch("services.lead_curation.logger")
    def test_curate_leads_logging(self, mock_logger, mock_openai_client, sample_events, sample_ai_response):
        """Test that logging works correctly."""
        mock_openai_client.chat_completion.return_value = sample_ai_response
        
        result = curate_leads(sample_events, openai_client=mock_openai_client)
        
        # Verify evaluation logging
        mock_logger.info.assert_any_call("Evaluating %d events for priority", 5)
        
        # Verify selection logging 
        mock_logger.info.assert_any_call("Selected %d priority events", 3)
        
        # Verify individual event logging (with context preview)
        expected_context_0 = sample_events[0].context[:50] + "..." if len(sample_events[0].context) > 50 else sample_events[0].context
        mock_logger.info.assert_any_call("Priority %d: %s", 1, expected_context_0)

    def test_curate_leads_uses_decision_model(self, mock_openai_client, sample_events):
        """Test that the correct model is used for decision making."""
        from config.settings import DECISION_MODEL
        
        mock_openai_client.chat_completion.return_value = "1"
        
        curate_leads(sample_events, openai_client=mock_openai_client)
        
        # Verify model parameter
        call_kwargs = mock_openai_client.chat_completion.call_args[1]
        assert call_kwargs["model"] == DECISION_MODEL

    def test_filter_leads_by_indices_edge_cases(self, sample_events):
        """Test edge cases in _filter_leads_by_indices helper."""
        from services.lead_curation import _filter_leads_by_indices
        
        # Test with duplicate numbers
        result = _filter_leads_by_indices("1, 1, 2", sample_events)
        assert len(result) == 3  # Should include duplicates
        assert result[0] == sample_events[0]
        assert result[1] == sample_events[0] 
        assert result[2] == sample_events[1]
        
        # Test with zero
        result = _filter_leads_by_indices("0, 1", sample_events)
        assert len(result) == 1  # Zero is invalid (should be 1-based)
        assert result[0] == sample_events[0]

    def test_curate_leads_fallback_behavior(self, mock_openai_client, sample_events):
        """Test fallback behavior when parsing fails."""
        mock_openai_client.chat_completion.return_value = ""  # Empty response
        
        result = curate_leads(sample_events, openai_client=mock_openai_client)
        
        # Should return top 3 as fallback
        assert len(result) == 3
        assert result == sample_events[:3]
