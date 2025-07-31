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
                discovered_lead="Climate Summit 2024: World leaders meet to discuss climate change solutions and carbon reduction targets.",
                sources=["https://example.com/discovery-climate-1", "https://example.com/discovery-climate-2"]
            ),
            Lead(
                discovered_lead="Tech Innovation Expo: Major technology companies showcase AI and renewable energy innovations.",
                sources=["https://example.com/discovery-tech-1"]
            ),
        ]

    @pytest.fixture
    def sample_research_response(self):
        """Sample research response from Perplexity."""
        content = ("The Climate Summit 2024 brings together world leaders from "
                "over 190 countries to address the escalating climate crisis. "
                "The summit focuses on implementing concrete measures to limit "
                "global warming to 1.5°C, "
                "with major discussions on renewable energy transition, carbon capture "
                "technologies, and climate finance for developing nations.")
        
        citations = [
            "https://example.com/climate-news",
            "https://example.com/summit-report"
        ]
        
        return content, citations

    @pytest.fixture
    def sample_malformed_research_response(self):
        """Sample malformed research response."""
        content = "Test report with incomplete data"
        citations = ["https://incomplete.example.com"]
        return content, citations

    def test_research_lead_success(self, mock_perplexity_client, sample_leads, sample_research_response):
        """Test successful lead research."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        enhanced_leads = research_lead(sample_leads, perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 2
        assert isinstance(enhanced_leads[0], Lead)
        # Check that original discovered_lead is preserved
        assert enhanced_leads[0].discovered_lead == sample_leads[0].discovered_lead
        # Check that report was added
        assert "Climate Summit 2024" in enhanced_leads[0].report
        assert "190 countries" in enhanced_leads[0].report
        
        # Check that sources match the citations from the research response
        expected_sources = [
            "https://example.com/climate-news",
            "https://example.com/summit-report"
        ]
        assert enhanced_leads[0].sources == expected_sources

        # Verify research was called for each lead
        assert mock_perplexity_client.lead_research.call_count == 2

    def test_research_lead_prompt_formatting(self, mock_perplexity_client, sample_leads, sample_research_response):
        """Test that research prompts are formatted correctly with lead discovered_leads directly."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        research_lead(sample_leads, perplexity_client=mock_perplexity_client)

        # Verify prompts were formatted with original lead discovered_leads (not search queries)
        call_args_list = mock_perplexity_client.lead_research.call_args_list

        # Check that both calls contain the original lead discovered_leads
        first_call_prompt = call_args_list[0][0][0]
        second_call_prompt = call_args_list[1][0][0]
        
        # Should contain lead discovered_leads directly since we're not using query formulation
        assert sample_leads[0].discovered_lead in first_call_prompt
        assert sample_leads[1].discovered_lead in second_call_prompt

    def test_research_lead_json_parsing(self, mock_perplexity_client, sample_leads):
        """Test parsing from research response."""
        content = "Detailed context about the lead including background information"
        citations = ["https://example.com/test", "https://example.com/analysis"]
        mock_perplexity_client.lead_research.return_value = content, citations

        enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        assert enhanced_leads[0].report == content
        assert enhanced_leads[0].sources == citations
        # Original discovered_lead should be preserved
        assert enhanced_leads[0].discovered_lead == sample_leads[0].discovered_lead

    def test_research_lead_malformed_json(self, mock_perplexity_client, sample_leads, sample_malformed_research_response):
        """Test handling of response with problematic content."""
        mock_perplexity_client.lead_research.return_value = sample_malformed_research_response

        enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        assert enhanced_leads[0].discovered_lead == sample_leads[0].discovered_lead
        assert enhanced_leads[0].report == "Test report with incomplete data"
        assert enhanced_leads[0].sources == ["https://incomplete.example.com"]
        # The original lead should be enhanced with the provided content and citations

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

        # Verify the logger was called with citation count information
        mock_logger.info.assert_any_call("  📊 Citations found: %d", 2)
        # Verify the logger was called with report length information
        mock_logger.info.assert_any_call("  📊 Report length: %d words", 47)

    def test_research_lead_with_fenced_response(self, mock_perplexity_client, sample_leads):
        """Test research with response that might contain markdown fences.

        Since the Perplexity client now returns a tuple of (content, citations),
        we need to test handling of markdown or other formatting in the response.
        """
        content = "Research context with ```markdown``` in it"
        citations = ["https://example.com"]
        mock_perplexity_client.lead_research.return_value = content, citations

        enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        # Should enhance the lead with the provided content and citations
        assert enhanced_leads[0].discovered_lead == sample_leads[0].discovered_lead
        assert enhanced_leads[0].report == content
        assert enhanced_leads[0].sources == citations

    def test_research_preserves_date(self, mock_perplexity_client):
        """Test that research preserves the original lead date."""
        lead_with_date = Lead(discovered_lead="Test lead", date="2024-01-15")
        content = "Context text"
        citations = ["https://example.com"]
        mock_perplexity_client.lead_research.return_value = content, citations

        enhanced_leads = research_lead([lead_with_date], perplexity_client=mock_perplexity_client)

        assert enhanced_leads[0].date == "2024-01-15"

    def test_research_lead_empty_discovery_sources(self, mock_perplexity_client):
        """Test research with lead that has empty sources from discovery."""
        lead_no_sources = Lead(
            discovered_lead="Lead with no discovery sources",
            sources=[]  # Empty sources from discovery
        )
        
        content = "Research context"
        citations = ["https://research-source-1.com", "https://research-source-2.com"]
        mock_perplexity_client.lead_research.return_value = content, citations

        enhanced_leads = research_lead([lead_no_sources], perplexity_client=mock_perplexity_client)

        # Should have the research citations
        assert enhanced_leads[0].sources == citations

    def test_research_lead_empty_values(self, mock_perplexity_client, sample_leads):
        """Test research with empty values in response."""
        content = ""
        citations = []
        mock_perplexity_client.lead_research.return_value = content, citations

        enhanced_leads = research_lead(sample_leads[:1], perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        # Verify handling of empty values
        assert enhanced_leads[0].report == ""
        assert enhanced_leads[0].sources == []
        # Original discovered_lead preserved
        assert enhanced_leads[0].discovered_lead == sample_leads[0].discovered_lead

    def test_research_lead_single_lead(self, mock_perplexity_client, sample_research_response):
        """Test research with single lead."""
        single_lead = [Lead(discovered_lead="Single Lead: Description of a single lead")]
        mock_perplexity_client.lead_research.return_value = sample_research_response

        enhanced_leads = research_lead(single_lead, perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        assert mock_perplexity_client.lead_research.call_count == 1

    def test_research_lead_source_combination(self, mock_perplexity_client):
        """Test that research uses the citations from the research response."""
        # Lead with existing sources from discovery
        lead_with_discovery_sources = Lead(
            discovered_lead="Test lead with discovery sources",
            sources=["https://discovery-source-1.com", "https://discovery-source-2.com"]
        )
        
        # Research response with new sources
        content = "Research context"
        citations = ["https://research-source-1.com", "https://research-source-2.com"]
        mock_perplexity_client.lead_research.return_value = content, citations

        enhanced_leads = research_lead([lead_with_discovery_sources], perplexity_client=mock_perplexity_client)

        # Should use the citations from the research response
        assert enhanced_leads[0].sources == citations

    def test_research_lead_citations_usage(self, mock_perplexity_client):
        """Test that citations from research response are used directly."""
        # Lead with discovery sources
        lead_with_sources = Lead(
            discovered_lead="Test lead",
            sources=["https://discovery-source.com", "https://another-discovery-source.com"]
        )
        
        # Research response with citations
        content = "Research context"
        citations = ["https://research-source-1.com", "https://research-source-2.com"]
        mock_perplexity_client.lead_research.return_value = content, citations

        enhanced_leads = research_lead([lead_with_sources], perplexity_client=mock_perplexity_client)

        # Should use the citations directly from the research response
        assert enhanced_leads[0].sources == citations

    def test_research_lead_client_error_propagation(self, mock_perplexity_client, sample_leads):
        """Test that client errors are properly propagated."""
        mock_perplexity_client.lead_research.side_effect = Exception("Research API Error")

        with pytest.raises(Exception, match="Research API Error"):
            research_lead(sample_leads, perplexity_client=mock_perplexity_client)
