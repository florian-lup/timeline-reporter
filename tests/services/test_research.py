"""Test suite for research service."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead, Story
from services import research_story


class TestResearchService:
    """Test suite for research service functions."""

    @pytest.fixture
    def mock_perplexity_client(self):
        """Mock Perplexity client for testing."""
        return Mock()

    @pytest.fixture
    def sample_leads(self):
        """Sample leads for testing."""
        return [
            Lead(
                tip="Climate Summit 2024: World leaders meet to discuss climate "
                "change solutions and carbon reduction targets.",
            ),
            Lead(
                tip="Tech Innovation Expo: Major technology companies showcase AI "
                "and renewable energy innovations.",
            ),
        ]

    @pytest.fixture
    def sample_research_response(self):
        """Sample research response from Perplexity."""
        return json.dumps(
            {
                "headline": "World Leaders Unite for Climate Action at Summit 2024",
                "summary": "Global climate summit reaches historic agreements on "
                "carbon reduction targets.",
                "body": "The Climate Summit 2024 has concluded with unprecedented "
                "cooperation between world leaders...",
                "sources": [
                    "https://example.com/climate-news",
                    "https://example.com/summit-report",
                ],
            }
        )

    @pytest.fixture
    def sample_malformed_research_response(self):
        """Sample malformed research response."""
        return '{"headline": "Test", "incomplete": json'

    def test_research_story_success(
        self, mock_perplexity_client, sample_leads, sample_research_response
    ):
        """Test successful story research."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        stories = research_story(sample_leads, perplexity_client=mock_perplexity_client)

        assert len(stories) == 2
        assert isinstance(stories[0], Story)
        assert (
            stories[0].headline
            == "World Leaders Unite for Climate Action at Summit 2024"
        )
        assert "carbon reduction targets" in stories[0].summary
        assert stories[0].body != ""
        assert stories[0].summary != ""

        # Verify research was called for each lead
        assert mock_perplexity_client.lead_research.call_count == 2

    def test_research_story_prompt_formatting(
        self, mock_perplexity_client, sample_leads, sample_research_response
    ):
        """Test that research prompts are formatted correctly."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        research_story(sample_leads, perplexity_client=mock_perplexity_client)

        # Verify prompts were formatted with lead tip
        call_args_list = mock_perplexity_client.lead_research.call_args_list

        # Check that both calls contain the lead tip
        first_call_prompt = call_args_list[0][0][0]
        second_call_prompt = call_args_list[1][0][0]
        assert sample_leads[0].tip in first_call_prompt
        assert sample_leads[1].tip in second_call_prompt

    def test_research_story_json_parsing(self, mock_perplexity_client, sample_leads):
        """Test JSON parsing from research response."""
        response = json.dumps(
            {
                "headline": "Test Headline",
                "summary": "Important summary",
                "body": "Detailed story body",
                "sources": ["https://example.com/test"],
            }
        )
        mock_perplexity_client.lead_research.return_value = response

        stories = research_story(
            sample_leads[:1], perplexity_client=mock_perplexity_client
        )

        assert len(stories) == 1
        assert stories[0].headline == "Test Headline"
        assert stories[0].summary == "Important summary"
        assert stories[0].body == "Detailed story body"
        assert stories[0].sources == ["https://example.com/test"]

    def test_research_story_malformed_json(
        self, mock_perplexity_client, sample_leads, sample_malformed_research_response
    ):
        """Test handling of malformed JSON response."""
        mock_perplexity_client.lead_research.return_value = (
            sample_malformed_research_response
        )

        with patch("services.story_research.logger") as mock_logger:
            stories = research_story(
                sample_leads[:1], perplexity_client=mock_perplexity_client
            )

        assert len(stories) == 1
        assert stories[0].headline == ""  # Default empty
        assert stories[0].summary == ""  # Default empty
        mock_logger.warning.assert_called()

    def test_research_story_empty_input(self, mock_perplexity_client):
        """Test research with empty lead list."""
        stories = research_story([], perplexity_client=mock_perplexity_client)

        assert stories == []
        mock_perplexity_client.lead_research.assert_not_called()

    @patch("services.story_research.logger")
    def test_research_story_logging(
        self,
        mock_logger,
        mock_perplexity_client,
        sample_leads,
        sample_research_response,
    ):
        """Test that research logs story count."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        research_story(sample_leads, perplexity_client=mock_perplexity_client)

        mock_logger.info.assert_called_with("Generated %d stories", 2)

    def test_research_story_with_fenced_json(
        self, mock_perplexity_client, sample_leads
    ):
        """Test research with JSON wrapped in markdown fences.

        Since the Perplexity client now uses structured output and returns clean JSON,
        fenced JSON should be treated as malformed input and result in an empty story.
        """
        fenced_response = """```json
        {
            "headline": "Research Headline",
            "summary": "Research Summary",
            "body": "Research Body",
            "sources": ["https://example.com"]
        }
        ```"""
        mock_perplexity_client.lead_research.return_value = fenced_response

        with patch("services.story_research.logger") as mock_logger:
            stories = research_story(
                sample_leads[:1], perplexity_client=mock_perplexity_client
            )

        assert len(stories) == 1
        # Should create empty story due to JSON parse failure
        assert stories[0].headline == ""
        assert stories[0].summary == ""
        assert stories[0].body == ""
        assert stories[0].sources == []
        mock_logger.warning.assert_called()

    def test_research_story_unicode_handling(
        self, mock_perplexity_client, sample_leads
    ):
        """Test research with Unicode characters."""
        unicode_response = json.dumps(
            {
                "headline": "Événement Important 🌍",
                "summary": "Résumé avec caractères spéciaux",
                "body": "Corps de l'story détaillé",
                "sources": ["https://example.com/français"],
            }
        )
        mock_perplexity_client.lead_research.return_value = unicode_response

        stories = research_story(
            sample_leads[:1], perplexity_client=mock_perplexity_client
        )

        assert len(stories) == 1
        assert "Résumé" in stories[0].summary
        assert stories[0].headline == "Événement Important 🌍"

    def test_research_story_missing_fields(self, mock_perplexity_client, sample_leads):
        """Test research with missing JSON fields."""
        response_missing_fields = json.dumps(
            {
                "headline": "Only Headline"
                # Missing summary, body, sources
            }
        )
        mock_perplexity_client.lead_research.return_value = response_missing_fields

        stories = research_story(
            sample_leads[:1], perplexity_client=mock_perplexity_client
        )

        assert len(stories) == 1
        assert stories[0].headline == "Only Headline"
        assert stories[0].summary == ""  # Default empty
        assert stories[0].body == ""  # Default empty
        assert stories[0].sources == []  # Default empty list

    def test_research_story_null_values(self, mock_perplexity_client, sample_leads):
        """Test research with null values in JSON."""
        response_null_values = json.dumps(
            {
                "headline": "Test Headline",
                "summary": None,
                "body": None,
                "sources": None,
            }
        )
        mock_perplexity_client.lead_research.return_value = response_null_values

        stories = research_story(
            sample_leads[:1], perplexity_client=mock_perplexity_client
        )

        assert len(stories) == 1
        # Verify handling of null values (converted to safe defaults)
        assert stories[0].headline == "Test Headline"
        assert stories[0].summary == ""  # None converted to empty string
        assert stories[0].body == ""  # None converted to empty string
        assert stories[0].sources == []  # None converted to empty list

    def test_research_story_single_lead(
        self, mock_perplexity_client, sample_research_response
    ):
        """Test research with single lead."""
        single_lead = [Lead(tip="Single Lead: Description of a single lead")]
        mock_perplexity_client.lead_research.return_value = sample_research_response

        stories = research_story(single_lead, perplexity_client=mock_perplexity_client)

        assert len(stories) == 1
        assert mock_perplexity_client.lead_research.call_count == 1

    def test_research_story_client_error_propagation(
        self, mock_perplexity_client, sample_leads
    ):
        """Test that client errors are properly propagated."""
        mock_perplexity_client.lead_research.side_effect = Exception(
            "Research API Error"
        )

        with pytest.raises(Exception, match="Research API Error"):
            research_story(sample_leads, perplexity_client=mock_perplexity_client)

    def test_parse_story_from_response_direct(self):
        """Test the _parse_story_from_response function directly."""
        from services.story_research import _parse_story_from_response

        # Test valid JSON
        valid_json = json.dumps(
            {
                "headline": "Direct Test",
                "summary": "Direct Summary",
                "body": "Direct Body",
                "sources": ["direct.com"],
            }
        )

        story = _parse_story_from_response(valid_json)
        assert isinstance(story, Story)
        assert story.headline == "Direct Test"

        # Test invalid JSON
        with patch("services.story_research.logger") as mock_logger:
            story = _parse_story_from_response("invalid json")
            assert story.headline == ""  # Should return empty Story
            mock_logger.warning.assert_called()

    def test_research_story_empty_strings_handling(
        self, mock_perplexity_client, sample_leads
    ):
        """Test research with empty string values."""
        empty_response = json.dumps(
            {"headline": "", "summary": "", "body": "", "sources": []}
        )
        mock_perplexity_client.lead_research.return_value = empty_response

        stories = research_story(
            sample_leads[:1], perplexity_client=mock_perplexity_client
        )

        assert len(stories) == 1
        assert stories[0].headline == ""
        assert stories[0].summary == ""  # None converted to empty string
        assert stories[0].body == ""
        assert stories[0].sources == []

    def test_research_story_date_preservation(
        self, mock_perplexity_client, sample_research_response
    ):
        """Test that lead dates are preserved in story research."""
        # Create lead with specific date
        lead_with_date = Lead(
            tip="Test Lead: A test lead description", date="2024-01-15"
        )

        # Modify the research response to include the lead date
        research_with_date = json.dumps(
            {
                "headline": "Breaking News Story",
                "summary": "Important lead summary",
                "body": "Full story body with detailed information.",
                "sources": [
                    "https://example.com/source1",
                    "https://example.com/source2",
                ],
                "date": "2024-01-15",  # Include date in response
            }
        )
        mock_perplexity_client.lead_research.return_value = research_with_date

        stories = research_story(
            [lead_with_date], perplexity_client=mock_perplexity_client
        )

        # Story should have the date from the JSON response
        assert stories[0].date == "2024-01-15"
