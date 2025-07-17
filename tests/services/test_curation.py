"""Test suite for lead curation service."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead
from services import curate_leads


class TestLeadCuration:
    """Test suite for lead curation service functions."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        return Mock()

    @pytest.fixture
    def sample_leads(self):
        """Sample leads for testing."""
        return [
            Lead(
                context="Climate Summit 2024: World leaders meet to discuss climate "
                "change solutions and carbon reduction targets.",
            ),
            Lead(
                context="Earthquake in Pacific: A 6.5 magnitude earthquake struck the "
                "Pacific region with minimal damage reported.",
            ),
            Lead(
                context="Tech Conference Announced: Major technology companies "
                "announce new AI developments at annual conference.",
            ),
            Lead(
                context="Economic Policy Update: Government announces new economic "
                "policies affecting global markets.",
            ),
            Lead(
                context="Space Mission Success: NASA successfully launches new Mars "
                "exploration mission.",
            ),
        ]

    def test_curate_leads_empty_input(self, mock_openai_client):
        """Test curate_leads with empty input."""
        result = curate_leads([], openai_client=mock_openai_client)

        assert result == []
        mock_openai_client.chat_completion.assert_not_called()

    def test_curate_leads_hybrid_basic(self, mock_openai_client, sample_leads):
        """Test basic functionality of curate_leads with hybrid method."""
        # Mock hybrid evaluation response
        evaluation_response = json.dumps([
            {
                "index": 1,
                "global_impact": 9,
                "long_term_consequences": 8,
                "public_interest": 8,
                "uniqueness": 7,
                "credibility": 9,
                "brief_reasoning": "Major climate policy"
            },
            {
                "index": 2,
                "global_impact": 8,
                "long_term_consequences": 6,
                "public_interest": 9,
                "uniqueness": 6,
                "credibility": 9,
                "brief_reasoning": "Natural disaster"
            },
            {
                "index": 3,
                "global_impact": 7,
                "long_term_consequences": 7,
                "public_interest": 8,
                "uniqueness": 8,
                "credibility": 8,
                "brief_reasoning": "Tech development"
            },
            {
                "index": 4,
                "global_impact": 6,
                "long_term_consequences": 7,
                "public_interest": 7,
                "uniqueness": 5,
                "credibility": 8,
                "brief_reasoning": "Economic policy"
            },
            {
                "index": 5,
                "global_impact": 6,
                "long_term_consequences": 8,
                "public_interest": 7,
                "uniqueness": 8,
                "credibility": 8,
                "brief_reasoning": "Space mission"
            }
        ])

        mock_openai_client.chat_completion.return_value = evaluation_response

        result = curate_leads(sample_leads, openai_client=mock_openai_client)

        # Should return some leads (exact number depends on scoring and diversity)
        assert len(result) >= 3
        assert len(result) <= 5

        # All returned leads should be from the original set
        for lead in result:
            assert lead in sample_leads

    def test_curate_leads_formats_correctly(self, mock_openai_client, sample_leads):
        """Test that leads are formatted correctly for AI evaluation."""
        # Mock response
        mock_openai_client.chat_completion.return_value = json.dumps([
            {"index": 1, "global_impact": 8, "long_term_consequences": 8,
             "public_interest": 8, "uniqueness": 8, "credibility": 8}
        ])

        curate_leads(sample_leads, openai_client=mock_openai_client)

        # Verify the method was called
        assert mock_openai_client.chat_completion.called

        # Check that the prompt contains numbered leads
        call_args = mock_openai_client.chat_completion.call_args[0][0]
        assert "1. Climate Summit 2024" in call_args
        assert "2. Earthquake in Pacific" in call_args

    @patch("services.lead_curation.logger")
    def test_curate_leads_logging(self, mock_logger, mock_openai_client, sample_leads):
        """Test that logging works correctly."""
        # Mock response
        mock_openai_client.chat_completion.return_value = json.dumps([
            {"index": 1, "global_impact": 8, "long_term_consequences": 8,
             "public_interest": 8, "uniqueness": 8, "credibility": 8}
        ])

        curate_leads(sample_leads, openai_client=mock_openai_client)

        # Verify evaluation logging
        mock_logger.info.assert_any_call("Evaluating %d leads for priority", 5)

        # Verify completion logging
        mock_logger.info.assert_any_call("Selected %d priority leads", 1)

    def test_curate_leads_uses_curation_model(self, mock_openai_client, sample_leads):
        """Test that the correct model is used for decision making."""
        from config.settings import CURATION_MODEL

        # Mock response
        mock_openai_client.chat_completion.return_value = json.dumps([
            {"index": 1, "global_impact": 8, "long_term_consequences": 8,
             "public_interest": 8, "uniqueness": 8, "credibility": 8}
        ])

        curate_leads(sample_leads, openai_client=mock_openai_client)

        # Verify model parameter was used in at least one call
        calls = mock_openai_client.chat_completion.call_args_list
        assert any(
            call.kwargs.get("model") == CURATION_MODEL
            for call in calls if call.kwargs
        )

    def test_curate_leads_fallback_behavior(self, mock_openai_client, sample_leads):
        """Test fallback behavior when evaluation fails."""
        # Mock invalid JSON response
        mock_openai_client.chat_completion.return_value = "Invalid JSON response"

        result = curate_leads(sample_leads, openai_client=mock_openai_client)

        # Should still return minimum number of leads due to fallback scoring
        assert len(result) >= 3
        assert all(lead in sample_leads for lead in result)
