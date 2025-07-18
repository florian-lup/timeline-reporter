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
                "context": "The Climate Summit 2024 brings together world leaders from "
                "over 190 countries to address the escalating climate crisis. The summit "
                "focuses on implementing concrete measures to limit global warming to 1.5°C, "
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
        return '{"context": "Test", "incomplete": json'

    def test_research_lead_success(
        self, mock_perplexity_client, sample_leads, sample_research_response
    ):
        """Test successful lead research."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        enhanced_leads = research_lead(sample_leads, perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 2
        assert isinstance(enhanced_leads[0], Lead)
        # Check that original tip is preserved
        assert enhanced_leads[0].tip == sample_leads[0].tip
        # Check that context was added
        assert "Climate Summit 2024" in enhanced_leads[0].context
        assert "190 countries" in enhanced_leads[0].context
        # Check that sources were added
        assert len(enhanced_leads[0].sources) == 2
        assert enhanced_leads[0].sources[0] == "https://example.com/climate-news"

        # Verify research was called for each lead
        assert mock_perplexity_client.lead_research.call_count == 2

    def test_research_lead_prompt_formatting(
        self, mock_perplexity_client, sample_leads, sample_research_response
    ):
        """Test that research prompts are formatted correctly."""
        mock_perplexity_client.lead_research.return_value = sample_research_response

        research_lead(sample_leads, perplexity_client=mock_perplexity_client)

        # Verify prompts were formatted with lead tip
        call_args_list = mock_perplexity_client.lead_research.call_args_list

        # Check that both calls contain the lead tip
        first_call_prompt = call_args_list[0][0][0]
        second_call_prompt = call_args_list[1][0][0]
        assert sample_leads[0].tip in first_call_prompt
        assert sample_leads[1].tip in second_call_prompt

    def test_research_lead_json_parsing(self, mock_perplexity_client, sample_leads):
        """Test JSON parsing from research response."""
        response = json.dumps(
            {
                "context": "Detailed context about the lead including background information",
                "sources": ["https://example.com/test", "https://example.com/analysis"],
            }
        )
        mock_perplexity_client.lead_research.return_value = response

        enhanced_leads = research_lead(
            sample_leads[:1], perplexity_client=mock_perplexity_client
        )

        assert len(enhanced_leads) == 1
        assert enhanced_leads[0].context == "Detailed context about the lead including background information"
        assert enhanced_leads[0].sources == ["https://example.com/test", "https://example.com/analysis"]
        # Original tip should be preserved
        assert enhanced_leads[0].tip == sample_leads[0].tip

    def test_research_lead_malformed_json(
        self, mock_perplexity_client, sample_leads, sample_malformed_research_response
    ):
        """Test handling of malformed JSON response."""
        mock_perplexity_client.lead_research.return_value = (
            sample_malformed_research_response
        )

        with patch("services.lead_research.logger") as mock_logger:
            enhanced_leads = research_lead(
                sample_leads[:1], perplexity_client=mock_perplexity_client
            )

        assert len(enhanced_leads) == 1
        # Should return original lead unchanged on parse error
        assert enhanced_leads[0].tip == sample_leads[0].tip
        assert enhanced_leads[0].context == ""  # Original empty context
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

        mock_logger.info.assert_called_with("Enhanced %d leads with research", 2)

    def test_research_lead_with_fenced_json(self, mock_perplexity_client, sample_leads):
        """Test research with JSON wrapped in markdown fences.

        Since the Perplexity client now uses structured output and returns clean JSON,
        fenced JSON should be treated as malformed input and result in the original lead.
        """
        fenced_response = """```json
        {
            "context": "Research context",
            "sources": ["https://example.com"]
        }
        ```"""
        mock_perplexity_client.lead_research.return_value = fenced_response

        with patch("services.lead_research.logger") as mock_logger:
            enhanced_leads = research_lead(
                sample_leads[:1], perplexity_client=mock_perplexity_client
            )

        assert len(enhanced_leads) == 1
        # Should return original lead due to JSON parse failure
        assert enhanced_leads[0].tip == sample_leads[0].tip
        assert enhanced_leads[0].context == ""
        assert enhanced_leads[0].sources == []
        mock_logger.warning.assert_called()

    def test_research_preserves_date(self, mock_perplexity_client):
        """Test that research preserves the original lead date."""
        lead_with_date = Lead(
            tip="Test lead",
            date="2024-01-15"
        )
        response = json.dumps({
            "context": "Context text",
            "sources": ["https://example.com"]
        })
        mock_perplexity_client.lead_research.return_value = response

        enhanced_leads = research_lead(
            [lead_with_date], perplexity_client=mock_perplexity_client
        )

        assert enhanced_leads[0].date == "2024-01-15"

    def test_research_lead_null_values(self, mock_perplexity_client, sample_leads):
        """Test research with null values in JSON."""
        response_null_values = json.dumps(
            {
                "context": None,
                "sources": None,
            }
        )
        mock_perplexity_client.lead_research.return_value = response_null_values

        enhanced_leads = research_lead(
            sample_leads[:1], perplexity_client=mock_perplexity_client
        )

        assert len(enhanced_leads) == 1
        # Verify handling of null values (converted to safe defaults)
        assert enhanced_leads[0].context == ""  # None converted to empty string
        assert enhanced_leads[0].sources == []  # None converted to empty list
        # Original tip preserved
        assert enhanced_leads[0].tip == sample_leads[0].tip

    def test_research_lead_single_lead(
        self, mock_perplexity_client, sample_research_response
    ):
        """Test research with single lead."""
        single_lead = [Lead(tip="Single Lead: Description of a single lead")]
        mock_perplexity_client.lead_research.return_value = sample_research_response

        enhanced_leads = research_lead(single_lead, perplexity_client=mock_perplexity_client)

        assert len(enhanced_leads) == 1
        assert mock_perplexity_client.lead_research.call_count == 1

    def test_research_lead_client_error_propagation(
        self, mock_perplexity_client, sample_leads
    ):
        """Test that client errors are properly propagated."""
        mock_perplexity_client.lead_research.side_effect = Exception(
            "Research API Error"
        )

        with pytest.raises(Exception, match="Research API Error"):
            research_lead(sample_leads, perplexity_client=mock_perplexity_client)
