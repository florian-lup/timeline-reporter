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
                    "title": "Climate Summit Announced: World leaders gather to discuss climate action and environmental policies."
                },
                {
                    "title": "Earthquake Hits Pacific Region: 6.2 magnitude earthquake causes minimal damage but raises tsunami concerns."
                },
            ]
        )

    @pytest.fixture
    def sample_politics_response(self):
        """Sample politics category response."""
        return json.dumps([{
            "title": "Presidential Election Update: Major political shift as new candidate enters the race with strong support."
        }])

    @pytest.fixture
    def sample_environment_response(self):
        """Sample environment category response."""
        return json.dumps([{
            "title": "Climate Summit Announced: World leaders gather to discuss climate action and environmental policies."
        }])

    @pytest.fixture
    def sample_entertainment_response(self):
        """Sample entertainment category response."""
        return json.dumps([{
            "title": "World Cup Final: Historic victory as underdog team wins championship in dramatic overtime."
        }])

    @pytest.fixture
    def sample_leads_with_fences(self):
        """Sample response wrapped in markdown fences."""
        response_data = [{
            "title": "Climate Summit Announced: World leaders gather to discuss climate action and set new environmental targets."
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
        assert "Presidential Election Update" in leads[0].title
        assert "Climate Summit Announced" in leads[1].title
        assert "World Cup Final" in leads[2].title

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
        assert "Presidential Election Update" in leads[0].title
        assert "World Cup Final" in leads[1].title

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
        assert "Presidential Election Update" in leads[0].title
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
        # Individual lead logging also happens - updated to match new format without source count
        mock_logger.info.assert_any_call(
            "    📋 Lead %d/%d - %s", 
            1, 1, "World Cup Final: Historic victory..."
        )

    def test_discover_leads_preserves_formatting(self, mock_perplexity_client):
        """Test that discovery preserves original formatting in title."""
        response_with_formatting = json.dumps([{
            "title": "  Spaced Title  : Summary with\nnewlines and extra   spaces"
        }])
        mock_perplexity_client.lead_discovery.side_effect = [
            response_with_formatting,
            "[]",
            "[]",
        ]

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert leads[0].title == "  Spaced Title  : Summary with\nnewlines and extra   spaces"  # Preserves original formatting

    def test_discover_leads_unicode_handling(self, mock_perplexity_client):
        """Test discovery with Unicode characters."""
        unicode_response = json.dumps([{
            "title": "🌍 Climate Summit: Conférence sur les émissions de carbone et les objectifs environnementaux"
        }])
        mock_perplexity_client.lead_discovery.side_effect = [
            "[]",
            unicode_response,
            "[]",
        ]

        leads = discover_leads(mock_perplexity_client)

        assert len(leads) == 1
        assert "🌍" in leads[0].title
        assert "émissions" in leads[0].title

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

        # Test with missing title field
        response_missing_field = json.dumps(
            [
                {"other_field": "Some value"}  # Missing title field
            ]
        )

        with pytest.raises(KeyError):
            _parse_leads_from_response(response_missing_field)

        # Test with empty title
        response_empty_title = json.dumps([{
            "title": ""
        }])

        leads = _parse_leads_from_response(response_empty_title)
        assert len(leads) == 1
        assert leads[0].title == ""
        
        # Test with valid title
        response_valid = json.dumps([{"title": "Test title"}])
        leads = _parse_leads_from_response(response_valid)
        assert len(leads) == 1
        assert leads[0].title == "Test title"

    def test_fence_regex_multiple_fences(self, mock_perplexity_client):
        """Test handling of multiple markdown fences.

        Since the Perplexity client now uses structured output and returns clean JSON,
        fenced JSON should be treated as malformed input and result in empty results.
        """
        response_multiple_fences = """
        Some text here
        ```json
                    [{"title": "Lead 1: Summary 1"}]
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
