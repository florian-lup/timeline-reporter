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
                    "tip": "Climate Summit Announced: World leaders gather to discuss climate action and environmental policies.",
                    "sources": ["https://example.com/climate-news", "https://example.com/summit-2024"]
                },
                {
                    "tip": "Earthquake Hits Pacific Region: 6.2 magnitude earthquake causes minimal damage but raises tsunami concerns.",
                    "sources": ["https://example.com/earthquake-report", "https://example.com/pacific-news"]
                },
            ]
        )

    @pytest.fixture
    def sample_politics_response(self):
        """Sample politics category response."""
        return json.dumps([{
            "tip": "Presidential Election Update: Major political shift as new candidate enters the race with strong support.",
            "sources": ["https://example.com/election-news", "https://example.com/political-update"]
        }])

    @pytest.fixture
    def sample_environment_response(self):
        """Sample environment category response."""
        return json.dumps([{
            "tip": "Climate Summit Announced: World leaders gather to discuss climate action and environmental policies.",
            "sources": ["https://example.com/climate-summit", "https://example.com/environmental-policy"]
        }])

    @pytest.fixture
    def sample_entertainment_response(self):
        """Sample entertainment category response."""
        return json.dumps([{
            "tip": "World Cup Final: Historic victory as underdog team wins championship in dramatic overtime.",
            "sources": ["https://example.com/world-cup", "https://example.com/sports-news"]
        }])

    @pytest.fixture
    def sample_leads_with_fences(self):
        """Sample response wrapped in markdown fences."""
        response_data = [{
            "tip": "Climate Summit Announced: World leaders gather to discuss climate action and set new environmental targets.",
            "sources": ["https://example.com/climate-fences", "https://example.com/summit-fences"]
        }]
        return f"```json\n{json.dumps(response_data)}\n```"

    def test_discover_leads_success(
        self,
        mock_perplexity_client,
        sample_politics_response,
        sample_environment_response,
        sample_entertainment_response,
    ):
        """Test successful lead discovery across all categories."""
        # Mock the three API calls
        mock_perplexity_client.lead_discovery.side_effect = [
            sample_politics_response,
            sample_environment_response,
            sample_entertainment_response,
        ]

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 3
        assert "Presidential Election Update" in leads[0].tip
        assert "Climate Summit Announced" in leads[1].tip
        assert "World Cup Final" in leads[2].tip
        
        # Check that sources are present from discovery
        assert len(leads[0].sources) == 2
        assert "https://example.com/election-news" in leads[0].sources
        assert len(leads[1].sources) == 2
        assert "https://example.com/climate-summit" in leads[1].sources
        assert len(leads[2].sources) == 2
        assert "https://example.com/world-cup" in leads[2].sources

        # Verify Perplexity client was called three times
        assert mock_perplexity_client.lead_discovery.call_count == 3

    def test_discover_leads_empty_responses(self, mock_perplexity_client):
        """Test discovery with empty responses from all categories."""
        mock_perplexity_client.lead_discovery.side_effect = ["[]", "[]", "[]"]

        leads = discover_leads(mock_perplexity_client)

        assert leads == []
        assert mock_perplexity_client.lead_discovery.call_count == 3

    def test_discover_leads_partial_failure(
        self,
        mock_perplexity_client,
        sample_politics_response,
        sample_entertainment_response,
    ):
        """Test discovery when one category fails but others succeed."""
        # Middle category fails
        mock_perplexity_client.lead_discovery.side_effect = [
            sample_politics_response,
            Exception("API Error"),
            sample_entertainment_response,
        ]

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 2
        assert "Presidential Election Update" in leads[0].tip
        assert "World Cup Final" in leads[1].tip

        # Verify error was logged
        mock_logger.error.assert_called()
        assert mock_perplexity_client.lead_discovery.call_count == 3

    def test_discover_leads_malformed_json(self, mock_perplexity_client, sample_politics_response):
        """Test discovery with malformed JSON in one category."""
        mock_perplexity_client.lead_discovery.side_effect = [
            sample_politics_response,
            '{"invalid": json}',
            "[]",
        ]

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert "Presidential Election Update" in leads[0].tip
        mock_logger.warning.assert_called()

    def test_discover_leads_json_with_fences(self, mock_perplexity_client, sample_leads_with_fences):
        """Test discovery with JSON wrapped in markdown fences.

        Since the Perplexity client now uses structured output and returns clean JSON,
        fenced JSON should be treated as malformed input and result in empty results.
        """
        mock_perplexity_client.lead_discovery.side_effect = [
            sample_leads_with_fences,
            "[]",
            "[]",
        ]

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert leads == []
        mock_logger.warning.assert_called()

    def test_discover_leads_non_list_response(self, mock_perplexity_client):
        """Test discovery when response is not a list."""
        mock_perplexity_client.lead_discovery.side_effect = [
            json.dumps({"error": "Not a list"}),
            "[]",
            "[]",
        ]

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert leads == []
        mock_logger.warning.assert_called_with("Expected JSON array, got %s", dict)

    @patch("services.lead_discovery.logger")
    def test_discover_leads_logging(
        self,
        mock_logger,
        mock_perplexity_client,
        sample_politics_response,
        sample_environment_response,
        sample_entertainment_response,
    ):
        """Test that discovery logs lead counts for each category."""
        mock_perplexity_client.lead_discovery.side_effect = [
            sample_politics_response,
            sample_environment_response,
            sample_entertainment_response,
        ]

        discover_leads(mock_perplexity_client)

        # Verify category-specific logging - updated to match new emoji-based format
        mock_logger.info.assert_any_call("  📰 Scanning %s sources...", "politics")
        mock_logger.info.assert_any_call("  ✓ %s: %d leads found", "Politics", 1)
        # Individual lead logging also happens - updated to match new format with source count
        mock_logger.info.assert_any_call(
            "    📋 Lead %d/%d - %s (sources: %d)", 
            1, 1, "World Cup Final: Historic victory...", 2
        )

    def test_discover_leads_preserves_formatting(self, mock_perplexity_client):
        """Test that discovery preserves original formatting in tip."""
        response_with_formatting = json.dumps([{
            "tip": "  Spaced Title  : Summary with\nnewlines and extra   spaces",
            "sources": ["https://example.com/formatted-news"]
        }])
        mock_perplexity_client.lead_discovery.side_effect = [
            response_with_formatting,
            "[]",
            "[]",
        ]

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert leads[0].tip == "  Spaced Title  : Summary with\nnewlines and extra   spaces"  # Preserves original formatting
        assert len(leads[0].sources) == 1
        assert leads[0].sources[0] == "https://example.com/formatted-news"

    def test_discover_leads_unicode_handling(self, mock_perplexity_client):
        """Test discovery with Unicode characters."""
        unicode_response = json.dumps([{
            "tip": "🌍 Climate Summit: Conférence sur les émissions de carbone et les objectifs environnementaux",
            "sources": ["https://example.com/unicode-news", "https://example.com/international-news"]
        }])
        mock_perplexity_client.lead_discovery.side_effect = [
            "[]",
            unicode_response,
            "[]",
        ]

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert "🌍" in leads[0].tip
        assert "émissions" in leads[0].tip
        assert len(leads[0].sources) == 2
        assert "https://example.com/unicode-news" in leads[0].sources

    def test_discover_leads_all_categories_fail(self, mock_perplexity_client):
        """Test when all category API calls fail."""
        mock_perplexity_client.lead_discovery.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            Exception("API Error 3"),
        ]

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert leads == []
        assert mock_logger.error.call_count == 3

    def test_discover_leads_uses_correct_instructions(self, mock_perplexity_client):
        """Test that discovery uses the correct category-specific instructions."""
        from config.discovery_config import (
            DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
            DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
            DISCOVERY_POLITICS_INSTRUCTIONS,
        )

        mock_perplexity_client.lead_discovery.side_effect = ["[]", "[]", "[]"]

        discover_leads(mock_perplexity_client)

        # Verify each category instruction was used
        calls = mock_perplexity_client.lead_discovery.call_args_list
        assert calls[0][0][0] == DISCOVERY_POLITICS_INSTRUCTIONS
        assert calls[1][0][0] == DISCOVERY_ENVIRONMENT_INSTRUCTIONS
        assert calls[2][0][0] == DISCOVERY_ENTERTAINMENT_INSTRUCTIONS

    def test_parse_leads_from_response_edge_cases(self):
        """Test edge cases in lead parsing."""
        from services.lead_discovery import _parse_leads_from_response

        # Test with missing fields
        response_missing_field = json.dumps(
            [
                {"title": "Only Title"}  # Missing tip field
            ]
        )

        with pytest.raises(KeyError):
            _parse_leads_from_response(response_missing_field)

        # Test with empty strings
        response_empty_strings = json.dumps([{
            "tip": "",
            "sources": []
        }])

        leads = _parse_leads_from_response(response_empty_strings)
        assert len(leads) == 1
        assert leads[0].tip == ""
        assert leads[0].sources == []
        
        # Test with missing sources field (should default to empty list)
        response_missing_sources = json.dumps([{"tip": "Test tip"}])
        leads = _parse_leads_from_response(response_missing_sources)
        assert len(leads) == 1
        assert leads[0].tip == "Test tip"
        assert leads[0].sources == []  # Should default to empty list

    def test_fence_regex_multiple_fences(self, mock_perplexity_client):
        """Test handling of multiple markdown fences.

        Since the Perplexity client now uses structured output and returns clean JSON,
        fenced JSON should be treated as malformed input and result in empty results.
        """
        response_multiple_fences = """
        Some text here
        ```json
        [{"tip": "Lead 1: Summary 1"}]
        ```
        More text
        ```
        Not JSON
        ```
        """
        mock_perplexity_client.lead_discovery.return_value = response_multiple_fences

        with patch("services.lead_discovery.logger") as mock_logger:
            leads = discover_leads(mock_perplexity_client)

        assert leads == []
        mock_logger.warning.assert_called()
