"""Test suite for decision service."""

import pytest
from unittest.mock import Mock, patch

from services import decide_events
from utils import Event


class TestDecisionService:
    """Test suite for decision service functions."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def sample_events(self):
        """Sample events for testing."""
        return [
            Event(
                title="Climate Summit 2024",
                summary="World leaders meet to discuss climate change solutions and carbon reduction targets."
            ),
            Event(
                title="Earthquake in Pacific",
                summary="A 6.5 magnitude earthquake struck the Pacific region with minimal damage reported."
            ),
            Event(
                title="Tech Conference Announced",
                summary="Major technology companies announce new AI developments at annual conference."
            ),
            Event(
                title="Economic Policy Update",
                summary="Government announces new economic policies affecting global markets."
            ),
            Event(
                title="Space Mission Success",
                summary="NASA successfully launches new Mars exploration mission."
            )
        ]

    @pytest.fixture
    def sample_ai_response(self):
        """Sample AI response selecting events."""
        return "1, 3, 5"  # Select events 1, 3, and 5

    def test_decide_events_success(self, mock_openai_client, sample_events, sample_ai_response):
        """Test successful event decision making."""
        mock_openai_client.chat_completion.return_value = sample_ai_response
        
        with patch('services.decision.DECISION_MODEL', 'test-decision-model'):
            result = decide_events(sample_events, openai_client=mock_openai_client)
        
        # Should return 3 selected events
        assert len(result) == 3
        assert result[0] == sample_events[0]  # Event 1
        assert result[1] == sample_events[2]  # Event 3  
        assert result[2] == sample_events[4]  # Event 5
        
        # Verify OpenAI client was called with correct parameters
        mock_openai_client.chat_completion.assert_called_once()
        call_args = mock_openai_client.chat_completion.call_args
        assert call_args[1]['model'] == 'test-decision-model'

    def test_decide_events_prompt_formatting(self, mock_openai_client, sample_events, sample_ai_response):
        """Test that decision prompt is properly formatted."""
        mock_openai_client.chat_completion.return_value = sample_ai_response
        
        decide_events(sample_events, openai_client=mock_openai_client)
        
        # Verify prompt contains numbered events
        call_args = mock_openai_client.chat_completion.call_args[0][0]
        assert "1. Title: Climate Summit 2024" in call_args
        assert "2. Title: Earthquake in Pacific" in call_args
        assert "3. Title: Tech Conference Announced" in call_args
        assert "evaluation criteria" in call_args.lower()
        assert "global impact" in call_args.lower()

    def test_decide_events_empty_list(self, mock_openai_client):
        """Test decision making with empty event list."""
        with patch('services.decision.logger') as mock_logger:
            result = decide_events([], openai_client=mock_openai_client)
        
        assert result == []
        mock_openai_client.chat_completion.assert_not_called()
        mock_logger.info.assert_called_with("No events to evaluate")

    def test_decide_events_single_event(self, mock_openai_client):
        """Test decision making with single event."""
        single_event = [Event(title="Solo Event", summary="Only event in list")]
        mock_openai_client.chat_completion.return_value = "1"
        
        result = decide_events(single_event, openai_client=mock_openai_client)
        
        assert len(result) == 1
        assert result[0] == single_event[0]

    @pytest.mark.parametrize("ai_response,expected_count", [
        ("1, 2, 3", 3),
        ("1", 1),
        ("2, 4", 2),
        ("1 3 5", 3),  # Space separated
        ("Events: 1, 2, and 4", 3),  # With extra text
        ("Select numbers 2 and 5", 2),  # With descriptive text
    ])
    def test_decide_events_various_response_formats(self, mock_openai_client, sample_events, ai_response, expected_count):
        """Test decision making with various AI response formats."""
        mock_openai_client.chat_completion.return_value = ai_response
        
        result = decide_events(sample_events, openai_client=mock_openai_client)
        
        assert len(result) == expected_count

    def test_decide_events_invalid_numbers(self, mock_openai_client, sample_events):
        """Test decision making with invalid event numbers."""
        # AI selects events that don't exist
        mock_openai_client.chat_completion.return_value = "1, 7, 10"  # 7 and 10 don't exist
        
        with patch('services.decision.logger') as mock_logger:
            result = decide_events(sample_events, openai_client=mock_openai_client)
        
        # Should only get event 1 (others are invalid)
        assert len(result) == 1
        assert result[0] == sample_events[0]
        
        # Should log warnings about invalid numbers
        mock_logger.warning.assert_called()

    def test_decide_events_no_valid_numbers(self, mock_openai_client, sample_events):
        """Test decision making when AI response has no valid numbers."""
        mock_openai_client.chat_completion.return_value = "No clear selection provided"
        
        with patch('services.decision.logger') as mock_logger:
            result = decide_events(sample_events, openai_client=mock_openai_client)
        
        # Should fallback to first 3 events
        assert len(result) == 3
        assert result == sample_events[:3]
        
        mock_logger.warning.assert_any_call(
            "No valid numbers in response, using fallback"
        )

    def test_decide_events_ai_error_handling(self, mock_openai_client, sample_events):
        """Test error handling when AI request fails."""
        mock_openai_client.chat_completion.side_effect = Exception("AI API Error")
        
        # Should propagate the exception
        with pytest.raises(Exception, match="AI API Error"):
            decide_events(sample_events, openai_client=mock_openai_client)

    def test_decide_events_preserves_original_objects(self, mock_openai_client, sample_events):
        """Test that decision service preserves original Event objects unchanged."""
        mock_openai_client.chat_completion.return_value = "1, 3"
        
        result = decide_events(sample_events, openai_client=mock_openai_client)
        
        # Should return exact same object instances
        assert result[0] is sample_events[0]
        assert result[1] is sample_events[2]
        
        # Objects should be unchanged
        assert result[0].title == "Climate Summit 2024"
        assert result[0].summary == "World leaders meet to discuss climate change solutions and carbon reduction targets."

    @patch('services.decision.logger')
    def test_logging_decision_service(self, mock_logger, mock_openai_client, sample_events, sample_ai_response):
        """Test that decision service logs properly."""
        mock_openai_client.chat_completion.return_value = sample_ai_response
        
        decide_events(sample_events, openai_client=mock_openai_client)
        
        # Verify logging
        mock_logger.info.assert_any_call(
            "Evaluating %d events for priority", 5
        )
        mock_logger.info.assert_any_call(
            "Selected %d priority events", 3
        )
        mock_logger.info.assert_any_call(
            "Priority %d: %s", 1, "Climate Summit 2024"
        )

    def test_decide_events_fallback_behavior(self, mock_openai_client, sample_events):
        """Test fallback behavior when parsing fails completely."""
        mock_openai_client.chat_completion.return_value = "Unable to parse this response"
        
        with patch('services.decision.logger') as mock_logger:
            result = decide_events(sample_events, openai_client=mock_openai_client)
        
        # Should fallback to first 3 events
        assert len(result) == 3
        assert result == sample_events[:3]
        
        mock_logger.warning.assert_any_call(
            "No valid numbers in response, using fallback"
        )

    def test_decide_events_partial_parsing_success(self, mock_openai_client, sample_events):
        """Test when some numbers are valid and some are invalid."""
        # Mix of valid (1, 3) and invalid (99) numbers
        mock_openai_client.chat_completion.return_value = "1, 99, 3, abc"
        
        with patch('services.decision.logger') as mock_logger:
            result = decide_events(sample_events, openai_client=mock_openai_client)
        
        # Should get the 2 valid selections
        assert len(result) == 2
        assert result[0] == sample_events[0]  # Event 1
        assert result[1] == sample_events[2]  # Event 3
        
        # Should log warnings for invalid numbers
        mock_logger.warning.assert_called()

    def test_decide_events_duplicate_selections(self, mock_openai_client, sample_events):
        """Test when AI selects the same event multiple times."""
        mock_openai_client.chat_completion.return_value = "1, 1, 2, 1, 3"  # Duplicates
        
        result = decide_events(sample_events, openai_client=mock_openai_client)
        
        # Should deduplicate automatically (since we're adding to a list, duplicates will appear)
        # But in practice, same Event object added multiple times
        assert len(result) == 5  # All selections added, including duplicates
        assert result[0] == sample_events[0]  # First "1"
        assert result[1] == sample_events[0]  # Second "1"  
        assert result[2] == sample_events[1]  # "2"
        assert result[3] == sample_events[0]  # Third "1"
        assert result[4] == sample_events[2]  # "3" 