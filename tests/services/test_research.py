"""Test suite for research service."""

import json
import pytest
from unittest.mock import Mock, patch

from services import research_events
from utils import Event, Article


class TestResearchService:
    """Test suite for research service functions."""

    @pytest.fixture
    def mock_perplexity_client(self):
        """Mock Perplexity client for testing."""
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
                title="Tech Innovation Expo",
                summary="Major technology companies showcase AI and renewable energy innovations."
            )
        ]

    @pytest.fixture
    def sample_research_responses(self):
        """Sample responses from Perplexity research."""
        return [
            json.dumps({
                "headline": "Global Climate Summit Sets Ambitious 2030 Targets",
                "summary": "World leaders at the 2024 Climate Summit agreed on unprecedented carbon reduction goals.",
                "story": "In a historic gathering, the 2024 Climate Summit concluded with ambitious commitments.",
                "sources": ["https://example.com/climate-summit", "https://example.com/carbon-targets"]
            }),
            json.dumps({
                "headline": "AI Revolution Takes Center Stage at Tech Expo",
                "summary": "The annual Tech Innovation Expo revealed groundbreaking AI technologies.",
                "story": "This year's Tech Innovation Expo showcased revolutionary AI applications.",
                "sources": ["https://example.com/tech-expo", "https://example.com/ai-innovations"]
            })
        ]

    @pytest.fixture
    def malformed_research_response(self):
        """Sample malformed response with markdown fences."""
        return """```json
        {
            "headline": "Breaking News Event",
            "summary": "Important summary",
            "story": "Full story content",
            "sources": ["https://example.com"]
        }
        ```"""

    def test_research_events_success(self, mock_perplexity_client, sample_events, sample_research_responses):
        """Test successful research of events."""
        mock_perplexity_client.research.side_effect = sample_research_responses
        
        with patch('services.research.ARTICLE_RESEARCH_TEMPLATE', 'Research this event: {event_summary}'):
            articles = research_events(sample_events, perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 2
        
        # Verify first article
        assert isinstance(articles[0], Article)
        assert articles[0].headline == "Global Climate Summit Sets Ambitious 2030 Targets"
        assert "carbon reduction goals" in articles[0].summary
        assert len(articles[0].sources) == 2
        assert articles[0].broadcast == b""  # Placeholder
        assert articles[0].reporter == ""    # Placeholder
        
        # Verify Perplexity was called correctly
        assert mock_perplexity_client.research.call_count == 2

    def test_research_events_prompt_formatting(self, mock_perplexity_client, sample_events, sample_research_responses):
        """Test that research prompts are properly formatted."""
        mock_perplexity_client.research.side_effect = sample_research_responses
        
        with patch('services.research.ARTICLE_RESEARCH_TEMPLATE', 'Research event: {event_summary}'):
            research_events(sample_events, perplexity_client=mock_perplexity_client)
        
        # Verify prompts were formatted with event summaries
        call_args = mock_perplexity_client.research.call_args_list
        assert len(call_args) == 2
        
        assert "Research event: " + sample_events[0].summary == call_args[0][0][0]
        assert "Research event: " + sample_events[1].summary == call_args[1][0][0]

    def test_research_events_with_markdown_fences(self, mock_perplexity_client, sample_events, malformed_research_response):
        """Test research with markdown fence-wrapped JSON."""
        mock_perplexity_client.research.return_value = malformed_research_response
        
        articles = research_events([sample_events[0]], perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 1
        assert articles[0].headline == "Breaking News Event"
        assert articles[0].summary == "Important summary"
        assert articles[0].story == "Full story content"
        assert articles[0].sources == ["https://example.com"]

    def test_research_events_malformed_json(self, mock_perplexity_client, sample_events):
        """Test research with malformed JSON response."""
        mock_perplexity_client.research.return_value = "invalid json content{"
        
        with patch('services.research.logger') as mock_logger:
            articles = research_events([sample_events[0]], perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 1
        # Should create article with fallback values
        assert articles[0].headline == ""
        assert articles[0].summary == ""
        assert articles[0].story == "invalid json content{"  # Raw response as story
        assert articles[0].sources == []
        
        mock_logger.warning.assert_called_once()

    def test_research_events_missing_fields(self, mock_perplexity_client, sample_events):
        """Test research with missing fields in response."""
        incomplete_response = json.dumps({
            "headline": "Only Headline",
            # Missing summary, story, sources
        })
        mock_perplexity_client.research.return_value = incomplete_response
        
        articles = research_events([sample_events[0]], perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 1
        assert articles[0].headline == "Only Headline"
        assert articles[0].summary == ""     # Default empty
        assert articles[0].story == ""       # Default empty
        assert articles[0].sources == []     # Default empty

    def test_research_events_empty_list(self, mock_perplexity_client):
        """Test research with empty event list."""
        with patch('services.research.logger') as mock_logger:
            articles = research_events([], perplexity_client=mock_perplexity_client)
        
        assert articles == []
        mock_perplexity_client.research.assert_not_called()
        mock_logger.info.assert_called_with("Generated %d articles.", 0)

    def test_research_events_unicode_content(self, mock_perplexity_client, sample_events):
        """Test research with unicode characters in response."""
        unicode_response = json.dumps({
            "headline": "Climate Summit 🌍 Results",
            "summary": "Leaders discuss émissions reduction",
            "story": "The summit in København addressed climate change",
            "sources": ["https://example.com/climate-🌍"]
        })
        mock_perplexity_client.research.return_value = unicode_response
        
        articles = research_events([sample_events[0]], perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 1
        assert "🌍" in articles[0].headline
        assert "émissions" in articles[0].summary
        assert "København" in articles[0].story
        assert "🌍" in articles[0].sources[0]

    @pytest.mark.parametrize("field_value", [
        "",  # Empty string
        "   ",  # Whitespace only
        "a" * 1000,  # Very long content
        "Multi\nLine\nContent",  # Multiline
        "Special chars: !@#$%^&*()",  # Special characters
    ])
    def test_research_events_various_field_values(self, mock_perplexity_client, sample_events, field_value):
        """Test research with various field values."""
        response = json.dumps({
            "headline": field_value,
            "summary": field_value,
            "story": field_value,
            "sources": [field_value]
        })
        mock_perplexity_client.research.return_value = response
        
        articles = research_events([sample_events[0]], perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 1
        assert articles[0].headline == field_value
        assert articles[0].summary == field_value
        assert articles[0].story == field_value
        assert articles[0].sources == [field_value]

    @patch('services.research.logger')
    def test_logging_research(self, mock_logger, mock_perplexity_client, sample_events, sample_research_responses):
        """Test that research logs properly."""
        mock_perplexity_client.research.side_effect = sample_research_responses
        
        research_events(sample_events, perplexity_client=mock_perplexity_client)
        
        # Verify debug logging for each event
        debug_calls = mock_logger.debug.call_args_list
        assert len(debug_calls) == 2
        
        # Verify info logging for final count
        mock_logger.info.assert_called_with("Generated %d articles.", 2)

    def test_research_events_article_structure(self, mock_perplexity_client, sample_events, sample_research_responses):
        """Test that generated articles have correct structure."""
        mock_perplexity_client.research.side_effect = sample_research_responses
        
        articles = research_events(sample_events, perplexity_client=mock_perplexity_client)
        
        for article in articles:
            # Verify all required fields are present
            assert hasattr(article, 'headline')
            assert hasattr(article, 'summary')
            assert hasattr(article, 'story')
            assert hasattr(article, 'sources')
            assert hasattr(article, 'broadcast')
            assert hasattr(article, 'reporter')
            
            # Verify types
            assert isinstance(article.headline, str)
            assert isinstance(article.summary, str)
            assert isinstance(article.story, str)
            assert isinstance(article.sources, list)
            assert isinstance(article.broadcast, bytes)
            assert isinstance(article.reporter, str)
            
            # Verify placeholder values for TTS fields
            assert article.broadcast == b""
            assert article.reporter == ""

    def test_research_events_perplexity_error_handling(self, mock_perplexity_client, sample_events):
        """Test error handling when Perplexity client fails."""
        mock_perplexity_client.research.side_effect = Exception("API Error")
        
        # Should propagate the exception
        with pytest.raises(Exception, match="API Error"):
            research_events(sample_events, perplexity_client=mock_perplexity_client)

    def test_parse_article_from_response_edge_cases(self, mock_perplexity_client, sample_events):
        """Test edge cases in article parsing."""
        # Test with null values in JSON
        response_with_nulls = json.dumps({
            "headline": None,
            "summary": None,
            "story": "Valid story",
            "sources": None
        })
        mock_perplexity_client.research.return_value = response_with_nulls
        
        articles = research_events([sample_events[0]], perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 1
        # Article class constructor doesn't convert None to empty string automatically
        # The service returns what's in the JSON, so None values remain None
        assert articles[0].headline is None   # None remains None
        assert articles[0].summary is None    # None remains None
        assert articles[0].story == "Valid story"
        assert articles[0].sources is None    # None remains None

    def test_research_events_large_response(self, mock_perplexity_client, sample_events):
        """Test research with very large response content."""
        large_story = "Content " * 10000  # Very large story
        large_response = json.dumps({
            "headline": "Large Article",
            "summary": "Summary of large article",
            "story": large_story,
            "sources": ["https://example.com"] * 100  # Many sources
        })
        mock_perplexity_client.research.return_value = large_response
        
        articles = research_events([sample_events[0]], perplexity_client=mock_perplexity_client)
        
        assert len(articles) == 1
        assert len(articles[0].story) == len(large_story)
        assert len(articles[0].sources) == 100 