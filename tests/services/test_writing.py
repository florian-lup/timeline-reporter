"""Test suite for story writing service."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead, Story
from services import write_stories


class TestWritingService:
    """Test suite for story writing service functions."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        return Mock()

    @pytest.fixture
    def sample_researched_leads(self):
        """Sample researched leads for testing."""
        return [
            Lead(
                tip="Climate Summit 2024: World leaders meet to discuss climate change",
                context=(
                    "The Climate Summit 2024 brings together world leaders from "
                    "over 190 countries to address the escalating climate crisis. "
                    "The summit focuses on implementing concrete measures to limit "
                    "global warming to 1.5°C, with major discussions on renewable "
                    "energy transition, carbon capture technologies, and climate "
                    "finance for developing nations. Key participants include the "
                    "US President, EU leaders, and representatives from major "
                    "developing economies. The summit aims to establish binding "
                    "commitments for carbon reduction by 2030."
                ),
                sources=[
                    "https://example.com/climate-summit-2024",
                    "https://example.com/un-climate-report",
                ],
                date="2024-01-15",
            ),
            Lead(
                tip="Tech Innovation Expo: AI breakthroughs announced",
                context=(
                    "The annual Tech Innovation Expo showcased groundbreaking AI "
                    "developments from major technology companies. Key announcements "
                    "included advances in natural language processing, autonomous "
                    "vehicle technology, and medical diagnostic AI. Companies "
                    "demonstrated AI systems capable of real-time language "
                    "translation and breakthrough cancer detection algorithms. "
                    "The expo highlighted the growing integration of AI in daily "
                    "life and raised important questions about ethics and regulation."
                ),
                sources=[
                    "https://example.com/tech-expo-2024",
                    "https://example.com/ai-breakthroughs",
                ],
                date="2024-01-16",
            ),
        ]

    @pytest.fixture
    def sample_writing_response(self):
        """Sample writing response from OpenAI."""
        return json.dumps(
            {
                "headline": ("World Leaders Unite at Climate Summit 2024 for Urgent Action"),
                "summary": (
                    "The Climate Summit 2024 has concluded with unprecedented "
                    "cooperation between world leaders from 190 countries, "
                    "establishing binding commitments to reduce carbon emissions "
                    "by 50% before 2030. The summit addressed critical climate "
                    "finance for developing nations "
                    "and accelerated renewable energy transition plans."
                ),
                "body": (
                    "The Climate Summit 2024 has concluded with historic agreements "
                    "that mark a turning point in global climate action. World leaders "
                    "from over 190 countries gathered to address the escalating "
                    "climate "
                    "crisis with unprecedented urgency and cooperation.\n\n"
                    "The summit's primary achievement was establishing binding "
                    "commitments for carbon reduction by 2030, with developed nations "
                    "pledging to cut emissions by 50%. Major discussions centered on "
                    "renewable energy transition, carbon capture technologies, and "
                    "crucial climate finance for developing nations.\n\n"
                    "Key participants, including the US President and EU leaders, "
                    "emphasized the critical importance of limiting global warming to "
                    "1.5°C. The agreements reached represent the most comprehensive "
                    "climate action plan in recent history, with implementation "
                    "beginning immediately."
                ),
            }
        )

    def test_write_stories_success(self, mock_openai_client, sample_researched_leads, sample_writing_response):
        """Test successful story writing."""
        mock_openai_client.chat_completion.return_value = sample_writing_response

        stories = write_stories(sample_researched_leads, openai_client=mock_openai_client)

        assert len(stories) == 2
        assert isinstance(stories[0], Story)
        assert stories[0].headline == ("World Leaders Unite at Climate Summit 2024 for Urgent Action")
        assert "unprecedented cooperation" in stories[0].summary
        assert "Climate Summit 2024 has concluded" in stories[0].body

        # Verify sources and date are preserved from lead
        assert stories[0].sources == sample_researched_leads[0].sources
        assert stories[0].date == sample_researched_leads[0].date

        # Verify OpenAI client was called for each lead
        assert mock_openai_client.chat_completion.call_count == 2

    def test_write_stories_openai_parameters(self, mock_openai_client, sample_researched_leads, sample_writing_response):
        """Test that OpenAI client is called with correct parameters."""
        mock_openai_client.chat_completion.return_value = sample_writing_response

        write_stories(sample_researched_leads[:1], openai_client=mock_openai_client)

        # Verify OpenAI client was called with correct parameters
        call_args = mock_openai_client.chat_completion.call_args
        assert call_args[1]["model"] == "gpt-4.1-2025-04-14"
        assert call_args[1]["response_format"] == {"type": "json_object"}

    def test_write_stories_prompt_formatting(self, mock_openai_client, sample_researched_leads, sample_writing_response):
        """Test that prompts are formatted correctly."""
        mock_openai_client.chat_completion.return_value = sample_writing_response

        write_stories(sample_researched_leads[:1], openai_client=mock_openai_client)

        # Verify prompt contains expected elements
        call_args = mock_openai_client.chat_completion.call_args
        prompt = call_args[0][0]  # First positional argument is the prompt

        # Should contain context but not tip or sources
        assert sample_researched_leads[0].context in prompt
        assert sample_researched_leads[0].date in prompt
        assert sample_researched_leads[0].tip not in prompt
        # Sources should not be in prompt
        assert "https://example.com" not in prompt

        # Should contain system prompt and JSON instruction
        assert "award-winning news journalist" in prompt.lower()
        assert "json object" in prompt.lower()

    def test_write_stories_json_parsing(self, mock_openai_client, sample_researched_leads):
        """Test JSON parsing from writing response."""
        response = json.dumps(
            {
                "headline": "Test Headline",
                "summary": "Important summary content",
                "body": "Detailed story body content",
            }
        )
        mock_openai_client.chat_completion.return_value = response

        stories = write_stories(sample_researched_leads[:1], openai_client=mock_openai_client)

        assert len(stories) == 1
        assert stories[0].headline == "Test Headline"
        assert stories[0].summary == "Important summary content"
        assert stories[0].body == "Detailed story body content"
        assert stories[0].sources == sample_researched_leads[0].sources

    def test_write_stories_json_parse_error(self, mock_openai_client, sample_researched_leads):
        """Test handling of malformed JSON response."""
        malformed_response = '{"headline": "Test", "incomplete": json'
        mock_openai_client.chat_completion.return_value = malformed_response

        with (
            patch("services.story_writing.logger") as mock_logger,
            pytest.raises(json.JSONDecodeError),
        ):
            write_stories(sample_researched_leads[:1], openai_client=mock_openai_client)

        # Verify error was logged
        mock_logger.error.assert_called_once()
        mock_logger.debug.assert_called_once()

    def test_write_stories_empty_input(self, mock_openai_client):
        """Test writing with empty lead list."""
        stories = write_stories([], openai_client=mock_openai_client)

        assert stories == []
        mock_openai_client.chat_completion.assert_not_called()

    @patch("services.story_writing.logger")
    def test_write_stories_logging(
        self,
        mock_logger,
        mock_openai_client,
        sample_researched_leads,
        sample_writing_response,
    ):
        """Test that writing logs story count."""
        mock_openai_client.chat_completion.return_value = sample_writing_response

        write_stories(sample_researched_leads, openai_client=mock_openai_client)

        # Verify the last call matches the final story completion log
        # The implementation logs each story individually, so check the last call
        mock_logger.info.assert_called_with(
            "  ✓ Story %d/%d completed - %s: '%s'",
            2,
            2,
            "Tech Innovation Expo: AI breakthroughs...",
            "World Leaders Unite at Climate Summit 2024 for Urgent Action",
        )

    def test_write_stories_missing_json_fields(self, mock_openai_client, sample_researched_leads):
        """Test writing with missing JSON fields."""
        response_missing_fields = json.dumps(
            {
                "headline": "Only Headline"
                # Missing summary and body
            }
        )
        mock_openai_client.chat_completion.return_value = response_missing_fields

        stories = write_stories(sample_researched_leads[:1], openai_client=mock_openai_client)

        assert len(stories) == 1
        assert stories[0].headline == "Only Headline"
        assert stories[0].summary == ""  # Default empty
        assert stories[0].body == ""  # Default empty

    def test_write_stories_empty_context(self, mock_openai_client):
        """Test writing with lead that has empty context."""
        lead_empty_context = Lead(
            tip="Empty context lead",
            context="",
            sources=["https://example.com"],
            date="2024-01-15",
        )

        response = json.dumps(
            {
                "headline": "Generated Headline",
                "summary": "Generated summary",
                "body": "Generated body",
            }
        )
        mock_openai_client.chat_completion.return_value = response

        stories = write_stories([lead_empty_context], openai_client=mock_openai_client)

        assert len(stories) == 1
        assert stories[0].sources == ["https://example.com"]

        # Verify prompt still gets formatted (with empty context)
        call_args = mock_openai_client.chat_completion.call_args
        prompt = call_args[0][0]
        assert "Context:" in prompt

    def test_write_stories_single_lead(self, mock_openai_client, sample_writing_response):
        """Test writing with single lead."""
        single_lead = [
            Lead(
                tip="Single test lead",
                context="Context for single lead test",
                sources=["https://single.com"],
                date="2024-01-20",
            )
        ]
        mock_openai_client.chat_completion.return_value = sample_writing_response

        stories = write_stories(single_lead, openai_client=mock_openai_client)

        assert len(stories) == 1
        assert mock_openai_client.chat_completion.call_count == 1

    def test_write_stories_client_error_propagation(self, mock_openai_client, sample_researched_leads):
        """Test that client errors are properly propagated."""
        mock_openai_client.chat_completion.side_effect = Exception("OpenAI API Error")

        with pytest.raises(Exception, match="OpenAI API Error"):
            write_stories(sample_researched_leads, openai_client=mock_openai_client)

    def test_parse_story_from_response_direct(self, sample_researched_leads):
        """Test the _parse_story_from_response function directly."""
        from services.story_writing import _parse_story_from_response

        # Test valid JSON
        valid_json = json.dumps(
            {
                "headline": "Direct Test Headline",
                "summary": "Direct test summary",
                "body": "Direct test body",
            }
        )

        story = _parse_story_from_response(valid_json, sample_researched_leads[0])
        assert isinstance(story, Story)
        assert story.headline == "Direct Test Headline"
        assert story.sources == sample_researched_leads[0].sources

        # Test invalid JSON
        with patch("services.story_writing.logger") as mock_logger:
            with pytest.raises(json.JSONDecodeError):
                _parse_story_from_response("invalid json", sample_researched_leads[0])
            mock_logger.error.assert_called()

    def test_write_stories_preserves_lead_attributes(self, mock_openai_client, sample_writing_response):
        """Test that lead attributes are properly preserved in stories."""
        lead_with_custom_date = Lead(
            tip="Custom date lead",
            context="Context with custom date",
            sources=["https://custom1.com", "https://custom2.com"],
            date="2024-12-25",
        )

        mock_openai_client.chat_completion.return_value = sample_writing_response

        stories = write_stories([lead_with_custom_date], openai_client=mock_openai_client)

        assert stories[0].date == "2024-12-25"
        assert stories[0].sources == ["https://custom1.com", "https://custom2.com"]
