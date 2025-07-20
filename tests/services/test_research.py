"""Test suite for research service."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead
from services import research_lead


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
                title="Climate Summit 2024: World leaders meet to discuss climate change solutions and carbon reduction targets.",
                sources=["https://example.com/discovery-climate-1", "https://example.com/discovery-climate-2"]
            ),
            Lead(
                title="Tech Innovation Expo: Major technology companies showcase AI and renewable energy innovations.",
                sources=["https://example.com/discovery-tech-1"]
            ),
        ]

    @pytest.fixture
    def sample_research_response(self):
        """Sample research response from Perplexity."""
        return json.dumps(
            {
                "report": "The Climate Summit 2024 brings together world leaders from "
                "over 190 countries to address the escalating climate crisis. "
                "The summit focuses on implementing concrete measures to limit "
                "global warming to 1.5°C, "
                "with major discussions on renewable energy transition, carbon capture "
                "technologies, and climate finance for developing nations.",
                "sources": [
                    "https://example.com/climate-news",
                    "https://example.com/summit-report",
                ],
            }
        )

    @pytest.fixture
    def sample_malformed_research_response(self):
        """Sample malformed research response."""
        return '{"report": "Test", "incomplete": json'

    def test_research_lead_success(self, mock_perplexity_client, sample_leads, sample_research_response):
        """Test successful lead research."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        enhanced_leads = research_lead(sample_leads, perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 2
        assert isinstance(enhanced_leads[0], Lead)
        # Check that original title is preserved
        assert enhanced_leads[0].title == sample_leads[0].title
        # Check that report was added
        assert "Climate Summit 2024" in enhanced_leads[0].report
        assert "190 countries" in enhanced_leads[0].report
        
        # Check that sources were combined - discovery sources + research sources
        expected_sources = set([
            "https://example.com/discovery-climate-1",
            "https://example.com/discovery-climate-2", 
            "https://example.com/climate-news",
            "https://example.com/summit-report"
        ])
        assert set(enhanced_leads[0].sources) == expected_sources
        assert len(enhanced_leads[0].sources) == 4

        # Verify research was called for each lead
        assert mock_perplexity_client.lead_research.call_count == 2

    def test_research_lead_prompt_formatting(self, mock_perplexity_client, sample_leads, sample_research_response):
        """Test that research prompts are formatted correctly with lead titles directly."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        research_lead(sample_leads, perplexity_client=mock_perplexity_client)

        # Verify prompts were formatted with original lead titles (not search queries)
        call_args_list = mock_perplexity_client.lead_research.call_args_list

        # Check that both calls contain the original lead titles
        first_call_prompt = call_args_list[0][0][0]
        second_call_prompt = call_args_list[1][0][0]
        
        # Should contain lead titles directly since we're not using query formulation
        assert sample_leads[0].title in first_call_prompt
        assert sample_leads[1].title in second_call_prompt

    def test_research_lead_json_parsing(self, mock_perplexity_client, sample_leads):
        """Test JSON parsing from research response."""
        response = json.dumps(
            {
                "report": ("Detailed context about the lead including background information"),
                "sources": ["https://example.com/test", "https://example.com/analysis"],
            }
        )
        mock_perplexity_client.lead_research.return_value = response

        enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        assert enhanced_leads[0].report == ("Detailed context about the lead including background information")
        assert enhanced_leads[0].sources == [
            "https://example.com/test",
            "https://example.com/analysis",
        ]
        # Original title should be preserved
        assert enhanced_leads[0].title == sample_leads[0].title

    def test_research_lead_malformed_json(self, mock_perplexity_client, sample_leads, sample_malformed_research_response):
        """Test handling of malformed JSON response."""
        mock_perplexity_client.lead_research.return_value = sample_malformed_research_response

        with patch("services.lead_research.logger") as mock_logger:
            enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        # Should return original lead unchanged on parse error
        assert enhanced_leads[0].title == sample_leads[0].title
        assert enhanced_leads[0].report == ""  # Original empty report
        assert enhanced_leads[0].sources == []  # Original empty sources
        mock_logger.warning.assert_called()

    def test_research_lead_empty_input(self, mock_perplexity_client):
        """Test research with empty lead list."""
        enhanced_leads = research_lead([], perplexity_client=mock_perplexity_client)

        assert enhanced_leads == []
        mock_perplexity_client.lead_research.assert_not_called()

    @patch("services.lead_research.logger")
    def test_research_lead_logging(
        self,
        mock_logger,
        mock_perplexity_client,
        sample_leads,
        sample_research_response,
    ):
        """Test that research logs lead count."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        research_lead(sample_leads, perplexity_client=mock_perplexity_client)

        # Verify the last call matches the final research completion log
        # The implementation logs each lead individually, so check the last call  
        # With source combination, this should be 3 sources (1 discovery + 2 research)
        mock_logger.info.assert_called_with("  📊 Sources found: %d", 3)

    def test_research_lead_with_fenced_json(self, mock_perplexity_client, sample_leads):
        """Test research with JSON wrapped in markdown fences.

        Since the Perplexity client now uses structured output and returns clean JSON,
        fenced JSON should be treated as malformed input and result in the original
        lead.
        """
        fenced_response = """```json
        {
            "report": "Research context",
            "sources": ["https://example.com"]
        }
        ```"""
        mock_perplexity_client.lead_research.return_value = fenced_response

        with patch("services.lead_research.logger") as mock_logger:
            enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        # Should return original lead due to JSON parse failure
        assert enhanced_leads[0].title == sample_leads[0].title
        assert enhanced_leads[0].report == ""
        assert enhanced_leads[0].sources == []
        mock_logger.warning.assert_called()

    def test_research_preserves_date(self, mock_perplexity_client):
        """Test that research preserves the original lead date."""
        lead_with_date = Lead(title="Test lead", date="2024-01-15")
        response = json.dumps({"report": "Context text", "sources": ["https://example.com"]})
        mock_perplexity_client.lead_research.return_value = response

        enhanced_leads = research_lead([lead_with_date], perplexity_client=mock_perplexity_client)

        assert enhanced_leads[0].date == "2024-01-15"

    def test_research_lead_empty_discovery_sources(self, mock_perplexity_client):
        """Test research with lead that has empty sources from discovery."""
        lead_no_sources = Lead(
            title="Lead with no discovery sources",
            sources=[]  # Empty sources from discovery
        )
        
        research_response = json.dumps({
            "report": "Research context",
            "sources": ["https://research-source-1.com", "https://research-source-2.com"]
        })
        mock_perplexity_client.lead_research.return_value = research_response

        enhanced_leads = research_lead([lead_no_sources], perplexity_client=mock_perplexity_client)

        # Should only have research sources
        assert len(enhanced_leads[0].sources) == 2
        assert set(enhanced_leads[0].sources) == {"https://research-source-1.com", "https://research-source-2.com"}

    def test_research_lead_null_values(self, mock_perplexity_client, sample_leads):
        """Test research with null values in JSON."""
        response_null_values = json.dumps(
            {
                "report": None,
                "sources": None,
            }
        )
        mock_perplexity_client.lead_research.return_value = response_null_values

        enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        # Verify handling of null values (converted to safe defaults)
        assert enhanced_leads[0].report == ""  # None converted to empty string
        assert enhanced_leads[0].sources == []  # None converted to empty list
        # Original title preserved
        assert enhanced_leads[0].title == sample_leads[0].title

    def test_research_lead_single_lead(self, mock_perplexity_client, sample_research_response):
        """Test research with single lead."""
        single_lead = [Lead(title="Single Lead: Description of a single lead")]
        mock_perplexity_client.lead_research.return_value = sample_research_response

        enhanced_leads = research_lead(single_lead, perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        assert mock_perplexity_client.lead_research.call_count == 1

    def test_research_lead_source_combination(self, mock_perplexity_client):
        """Test that research combines existing sources from discovery with new research sources."""
        # Lead with existing sources from discovery
        lead_with_discovery_sources = Lead(
            title="Test lead with discovery sources",
            sources=["https://discovery-source-1.com", "https://discovery-source-2.com"]
        )
        
        # Research response with new sources
        research_response = json.dumps({
            "report": "Research context",
            "sources": ["https://research-source-1.com", "https://research-source-2.com"]
        })
        mock_perplexity_client.lead_research.return_value = research_response

        enhanced_leads = research_lead([lead_with_discovery_sources], perplexity_client=mock_perplexity_client)

        # Should combine all sources without duplicates
        expected_sources = [
            "https://discovery-source-1.com",
            "https://discovery-source-2.com", 
            "https://research-source-1.com",
            "https://research-source-2.com"
        ]
        assert len(enhanced_leads[0].sources) == 4
        assert set(enhanced_leads[0].sources) == set(expected_sources)

    def test_research_lead_duplicate_source_removal(self, mock_perplexity_client):
        """Test that duplicate sources are removed when combining discovery and research sources."""
        # Lead with discovery sources
        lead_with_sources = Lead(
            title="Test lead",
            sources=["https://duplicate-source.com", "https://discovery-only.com"]
        )
        
        # Research response with overlapping sources
        research_response = json.dumps({
            "report": "Research context",
            "sources": ["https://duplicate-source.com", "https://research-only.com"]
        })
        mock_perplexity_client.lead_research.return_value = research_response

        enhanced_leads = research_lead([lead_with_sources], perplexity_client=mock_perplexity_client)

        # Should have 3 unique sources (duplicate removed)
        expected_sources = [
            "https://duplicate-source.com",
            "https://discovery-only.com",
            "https://research-only.com"
        ]
        assert len(enhanced_leads[0].sources) == 3
        assert set(enhanced_leads[0].sources) == set(expected_sources)

    def test_research_lead_client_error_propagation(self, mock_perplexity_client, sample_leads):
        """Test that client errors are properly propagated."""
        mock_perplexity_client.lead_research.side_effect = Exception("Research API Error")

        with pytest.raises(Exception, match="Research API Error"):
            research_lead(sample_leads, perplexity_client=mock_perplexity_client)
