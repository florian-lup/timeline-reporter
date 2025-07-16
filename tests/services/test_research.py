"""Test suite for research service."""

import json
from unittest.mock import Mock, patch

import pytest

from services import research_articles
from models import Lead, Story


class TestResearchService:
    """Test suite for research service functions."""

    @pytest.fixture
    def mock_perplexity_client(self):
        """Mock Perplexity client for testing."""
        return Mock()

    @pytest.fixture
    def sample_events(self):
        """Sample events for testing."""
        return [
            Lead(
                context="Climate Summit 2024: World leaders meet to discuss climate change solutions and carbon reduction targets.",
            ),
            Lead(
                context="Tech Innovation Expo: Major technology companies showcase AI and renewable energy innovations.",
            ),
        ]

    @pytest.fixture
    def sample_research_response(self):
        """Sample research response from Perplexity."""
        return json.dumps({
            "headline": "World Leaders Unite for Climate Action at Summit 2024",
            "summary": "Global climate summit reaches historic agreements on carbon reduction targets.",
            "body": "The Climate Summit 2024 has concluded with unprecedented cooperation between world leaders...",
            "sources": [
                "https://example.com/climate-news",
                "https://example.com/summit-report"
            ]
        })

    @pytest.fixture
    def sample_malformed_research_response(self):
        """Sample malformed research response."""
        return '{"headline": "Test", "incomplete": json'

    def test_research_articles_success(
        self, mock_perplexity_client, sample_events, sample_research_response
    ):
        """Test successful article research."""
        mock_perplexity_client.research.return_value = sample_research_response

        articles = research_articles(sample_events, perplexity_client=mock_perplexity_client)

        assert len(articles) == 2
        assert isinstance(articles[0], Story)
        assert articles[0].headline == "World Leaders Unite for Climate Action at Summit 2024"
        assert "carbon reduction targets" in articles[0].summary
        assert articles[0].body != ""
        assert articles[0].summary != ""

        # Verify research was called for each event
        assert mock_perplexity_client.research.call_count == 2

    def test_research_articles_prompt_formatting(
        self, mock_perplexity_client, sample_events, sample_research_response
    ):
        """Test that research prompts are formatted correctly."""
        mock_perplexity_client.research.return_value = sample_research_response

        research_articles(sample_events, perplexity_client=mock_perplexity_client)

        # Verify prompts were formatted with event context
        call_args_list = mock_perplexity_client.research.call_args_list
        
        # Check that both calls contain the event context
        first_call_prompt = call_args_list[0][0][0]
        second_call_prompt = call_args_list[1][0][0]
        assert sample_events[0].context in first_call_prompt
        assert sample_events[1].context in second_call_prompt

    def test_research_articles_json_parsing(
        self, mock_perplexity_client, sample_events
    ):
        """Test JSON parsing from research response."""
        response = json.dumps({
            "headline": "Test Headline",
            "summary": "Important summary",
            "body": "Detailed article body",
            "sources": ["https://example.com/test"]
        })
        mock_perplexity_client.research.return_value = response

        articles = research_articles(sample_events[:1], perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        assert articles[0].headline == "Test Headline"
        assert articles[0].summary == "Important summary"
        assert articles[0].body == "Detailed article body"
        assert articles[0].sources == ["https://example.com/test"]

    def test_research_articles_malformed_json(
        self, mock_perplexity_client, sample_events, sample_malformed_research_response
    ):
        """Test handling of malformed JSON response."""
        mock_perplexity_client.research.return_value = sample_malformed_research_response

        with patch("services.article_research.logger") as mock_logger:
            articles = research_articles(sample_events[:1], perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        assert articles[0].headline == ""  # Default empty
        assert articles[0].summary == ""  # Default empty
        mock_logger.warning.assert_called()

    def test_research_articles_empty_input(self, mock_perplexity_client):
        """Test research with empty event list."""
        articles = research_articles([], perplexity_client=mock_perplexity_client)

        assert articles == []
        mock_perplexity_client.research.assert_not_called()

    @patch("services.article_research.logger")
    def test_research_articles_logging(
        self, mock_logger, mock_perplexity_client, sample_events, sample_research_response
    ):
        """Test that research logs article count."""
        mock_perplexity_client.research.return_value = sample_research_response

        research_articles(sample_events, perplexity_client=mock_perplexity_client)

        mock_logger.info.assert_called_with("Generated %d articles", 2)

    def test_research_articles_with_fenced_json(self, mock_perplexity_client, sample_events):
        """Test research with JSON wrapped in markdown fences."""
        fenced_response = '''```json
        {
            "headline": "Research Headline",
            "summary": "Research Summary",
            "body": "Research Body",
            "sources": ["https://example.com"]
        }
        ```'''
        mock_perplexity_client.research.return_value = fenced_response

        articles = research_articles(sample_events[:1], perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        assert articles[0].headline == "Research Headline"

    def test_research_articles_unicode_handling(self, mock_perplexity_client, sample_events):
        """Test research with Unicode characters."""
        unicode_response = json.dumps({
            "headline": "Événement Important 🌍",
            "summary": "Résumé avec caractères spéciaux",
            "body": "Corps de l'article détaillé",
            "sources": ["https://example.com/français"]
        })
        mock_perplexity_client.research.return_value = unicode_response

        articles = research_articles(sample_events[:1], perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        assert "Résumé" in articles[0].summary
        assert articles[0].headline == "Événement Important 🌍"

    def test_research_articles_missing_fields(self, mock_perplexity_client, sample_events):
        """Test research with missing JSON fields."""
        response_missing_fields = json.dumps({
            "headline": "Only Headline"
            # Missing summary, body, sources
        })
        mock_perplexity_client.research.return_value = response_missing_fields

        articles = research_articles(sample_events[:1], perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        assert articles[0].headline == "Only Headline"
        assert articles[0].summary == ""  # Default empty
        assert articles[0].body == ""     # Default empty
        assert articles[0].sources == []  # Default empty list

    def test_research_articles_null_values(self, mock_perplexity_client, sample_events):
        """Test research with null values in JSON."""
        response_null_values = json.dumps({
            "headline": "Test Headline",
            "summary": None,
            "body": None,
            "sources": None
        })
        mock_perplexity_client.research.return_value = response_null_values

        articles = research_articles(sample_events[:1], perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        # Verify handling of null values (Story constructor allows None)
        assert articles[0].headline == "Test Headline"
        assert articles[0].summary is None  # None values preserved
        assert articles[0].body is None
        assert articles[0].sources is None

    def test_research_articles_single_event(self, mock_perplexity_client, sample_research_response):
        """Test research with single event."""
        single_event = [Lead(context="Single Event: Description of a single event")]
        mock_perplexity_client.research.return_value = sample_research_response

        articles = research_articles(single_event, perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        assert mock_perplexity_client.research.call_count == 1

    def test_research_articles_client_error_propagation(self, mock_perplexity_client, sample_events):
        """Test that client errors are properly propagated."""
        mock_perplexity_client.research.side_effect = Exception("Research API Error")

        with pytest.raises(Exception, match="Research API Error"):
            research_articles(sample_events, perplexity_client=mock_perplexity_client)

    def test_parse_article_from_response_direct(self):
        """Test the _parse_article_from_response function directly."""
        from services.article_research import _parse_article_from_response

        # Test valid JSON
        valid_json = json.dumps({
            "headline": "Direct Test",
            "summary": "Direct Summary",
            "body": "Direct Body",
            "sources": ["direct.com"]
        })
        
        article = _parse_article_from_response(valid_json)
        assert isinstance(article, Story)
        assert article.headline == "Direct Test"

        # Test invalid JSON
        with patch("services.article_research.logger") as mock_logger:
            article = _parse_article_from_response("invalid json")
            assert article.headline == ""  # Should return empty Story
            mock_logger.warning.assert_called()

    def test_research_articles_empty_strings_handling(self, mock_perplexity_client, sample_events):
        """Test research with empty string values."""
        empty_response = json.dumps({
            "headline": "",
            "summary": "",
            "body": "",
            "sources": []
        })
        mock_perplexity_client.research.return_value = empty_response

        articles = research_articles(sample_events[:1], perplexity_client=mock_perplexity_client)

        assert len(articles) == 1
        assert articles[0].headline == ""
        assert articles[0].summary == ""  # None converted to empty string
        assert articles[0].body == ""
        assert articles[0].sources == []

    def test_research_articles_date_preservation(self, mock_perplexity_client, sample_research_response):
        """Test that event dates are preserved in article research."""
        # Create event with specific date
        event_with_date = Lead(
            context="Test Event: A test event description",
            date="2024-01-15"
        )
        
        # Modify the research response to include the event date
        research_with_date = json.dumps({
            "headline": "Breaking News Story",
            "summary": "Important event summary",
            "body": "Full article body with detailed information.",
            "sources": ["https://example.com/source1", "https://example.com/source2"],
            "date": "2024-01-15"  # Include date in response
        })
        mock_perplexity_client.research.return_value = research_with_date

        articles = research_articles([event_with_date], perplexity_client=mock_perplexity_client)

        # Article should have the date from the JSON response
        assert articles[0].date == "2024-01-15"
