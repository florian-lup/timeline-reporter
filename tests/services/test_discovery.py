"""Test suite for discovery service."""

import json
from unittest.mock import patch

import pytest

from services import discover_leads


class TestDiscoveryService:
    """Test suite for discovery service functions."""

    @pytest.fixture
    def mock_perplexity_client(self):
        """Mock Perplexity client for testing."""
        from unittest.mock import Mock

        return Mock()

    @pytest.fixture
    def sample_discovery_response(self):
        """Sample discovery response JSON."""
        return json.dumps(
            [
                {
                    "context": "Climate Summit Announced: World leaders gather to discuss climate action and environmental policies."
                },
                {
                    "context": "Earthquake Hits Pacific Region: 6.2 magnitude earthquake causes minimal damage but raises tsunami concerns."
                },
            ]
        )

    @pytest.fixture
    def sample_leads_with_fences(self):
        """Sample response wrapped in markdown fences."""
        response_data = [
            {
                "context": "Climate Summit Announced: World leaders gather to discuss climate action and set new environmental targets."
            }
        ]
        return f"```json\n{json.dumps(response_data)}\n```"

    def test_discover_leads_success(
        self, mock_perplexity_client, sample_discovery_response
    ):
        """Test successful lead discovery."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 2
        assert "Climate Summit Announced" in leads[0].context
        assert "World leaders gather" in leads[0].context
        assert "Earthquake Hits Pacific Region" in leads[1].context

        # Verify Perplexity client was called
        mock_perplexity_client.deep_research.assert_called_once()

    def test_discover_leads_empty_response(self, mock_perplexity_client):
        """Test discovery with empty response."""
        mock_perplexity_client.deep_research.return_value = "[]"

        leads = discover_leads(mock_perplexity_client)

        assert leads == []

    def test_discover_leads_malformed_json(self, mock_perplexity_client):
        """Test discovery with malformed JSON."""
        mock_perplexity_client.deep_research.return_value = '{"invalid": json}'

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert leads == []
        mock_logger.warning.assert_called()

    def test_discover_leads_json_with_fences(
        self, mock_perplexity_client, sample_leads_with_fences
    ):
        """Test discovery with JSON wrapped in markdown fences."""
        mock_perplexity_client.deep_research.return_value = sample_leads_with_fences

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert "Climate Summit Announced" in leads[0].context

    def test_discover_leads_non_list_response(self, mock_perplexity_client):
        """Test discovery when response is not a list."""
        mock_perplexity_client.deep_research.return_value = json.dumps(
            {"error": "Not a list"}
        )

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert leads == []
        mock_logger.warning.assert_called_with("Expected JSON array, got %s", dict)

    @patch("services.lead_discovery.logger")
    def test_discover_leads_logging(
        self, mock_logger, mock_perplexity_client, sample_discovery_response
    ):
        """Test that discovery logs lead count."""
        mock_perplexity_client.deep_research.return_value = sample_discovery_response

        discover_leads(mock_perplexity_client)

        mock_logger.info.assert_called_with("Discovered %d leads", 2)

    def test_discover_leads_preserves_formatting(self, mock_perplexity_client):
        """Test that discovery preserves original formatting in context."""
        response_with_formatting = json.dumps(
            [{"context": "  Spaced Title  : Summary with\nnewlines and extra   spaces"}]
        )
        mock_perplexity_client.deep_research.return_value = response_with_formatting

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert (
            leads[0].context
            == "  Spaced Title  : Summary with\nnewlines and extra   spaces"
        )  # Preserves original formatting

    def test_discover_leads_unicode_handling(self, mock_perplexity_client):
        """Test discovery with Unicode characters."""
        unicode_response = json.dumps(
            [
                {
                    "context": "🌍 Climate Summit: Conférence sur les émissions de carbone et les objectifs environnementaux"
                }
            ]
        )
        mock_perplexity_client.deep_research.return_value = unicode_response

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert "🌍" in leads[0].context
        assert "émissions" in leads[0].context

    def test_discover_leads_client_error_propagation(self, mock_perplexity_client):
        """Test that client errors are properly propagated."""
        mock_perplexity_client.deep_research.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            discover_leads(mock_perplexity_client)

    def test_discover_leads_uses_discovery_instructions(self, mock_perplexity_client):
        """Test that discovery uses the correct instructions."""
        from config import DISCOVERY_INSTRUCTIONS

        mock_perplexity_client.deep_research.return_value = "[]"

        discover_leads(mock_perplexity_client)

        mock_perplexity_client.deep_research.assert_called_once_with(
            DISCOVERY_INSTRUCTIONS
        )

    def test_parse_leads_from_response_edge_cases(self):
        """Test edge cases in lead parsing."""
        from services.lead_discovery import _parse_leads_from_response

        # Test with missing fields
        response_missing_field = json.dumps(
            [
                {"title": "Only Title"}  # Missing context field
            ]
        )

        with pytest.raises(KeyError):
            _parse_leads_from_response(response_missing_field)

        # Test with empty strings
        response_empty_strings = json.dumps([{"context": ""}])

        leads = _parse_leads_from_response(response_empty_strings)
        assert len(leads) == 1
        assert leads[0].context == ""

    def test_fence_regex_multiple_fences(self, mock_perplexity_client):
        """Test handling of multiple markdown fences."""
        response_multiple_fences = """
        Some text here
        ```json
        [{"context": "Lead 1: Summary 1"}]
        ```
        More text
        ```
        Not JSON
        ```
        """
        mock_perplexity_client.deep_research.return_value = response_multiple_fences

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert leads[0].context == "Lead 1: Summary 1"
