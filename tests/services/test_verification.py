"""Test suite for lead verification service."""

import json
from unittest.mock import Mock, patch

import pytest

from clients import OpenAIClient
from config.verification_config import (
    MIN_CONTEXT_RELEVANCE_SCORE,
    MIN_SOURCE_CREDIBILITY_SCORE,
    MIN_TOTAL_SCORE,
)
from models import Lead
from services.lead_verification import (
    _evaluate_lead_credibility,
    _verify_lead_credibility,
    verify_leads,
)


class TestVerifyLeads:
    """Test suite for verify_leads function."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        return Mock(spec=OpenAIClient)

    @pytest.fixture
    def sample_leads(self):
        """Sample leads for testing."""
        return [
            Lead(
                title="Breaking: Tech company announces merger",
                date="2024-01-15",
                context="Tech company XYZ announced a merger with ABC Corp",
                sources=["https://reuters.com/tech", "https://bloomberg.com/business"],
            ),
            Lead(
                title="Local event happening",
                date="2024-01-15",
                context="Small local event with minimal details",
                sources=["https://localblog.com"],
            ),
            Lead(
                title="Major policy change",
                date="2024-01-15",
                context="Government announces significant policy changes",
                sources=["https://gov.official", "https://bbc.com/news"],
            ),
        ]

    def test_verify_leads_all_pass(self, mock_openai_client, sample_leads):
        """Test verify_leads when all leads pass verification."""
        with patch("services.lead_verification._verify_lead_credibility", return_value=True):
            result = verify_leads(sample_leads, openai_client=mock_openai_client)

            assert len(result) == 3
            assert result == sample_leads

    def test_verify_leads_mixed_results(self, mock_openai_client, sample_leads):
        """Test verify_leads with mixed pass/fail results."""
        # First and third leads pass, second fails
        side_effects = [True, False, True]

        with patch(
            "services.lead_verification._verify_lead_credibility",
            side_effect=side_effects,
        ):
            result = verify_leads(sample_leads, openai_client=mock_openai_client)

            assert len(result) == 2
            assert result[0] == sample_leads[0]
            assert result[1] == sample_leads[2]

    def test_verify_leads_all_fail(self, mock_openai_client, sample_leads):
        """Test verify_leads when all leads fail verification."""
        with patch("services.lead_verification._verify_lead_credibility", return_value=False):
            result = verify_leads(sample_leads, openai_client=mock_openai_client)

            assert len(result) == 0
            assert result == []

    def test_verify_leads_empty_list(self, mock_openai_client):
        """Test verify_leads with empty list."""
        result = verify_leads([], openai_client=mock_openai_client)

        assert len(result) == 0
        assert result == []

    def test_verify_leads_long_title_truncation(self, mock_openai_client):
        """Test that long titles are truncated in log messages."""
        long_title = "x" * 100  # Exceeds MAX_TIP_DISPLAY_LENGTH of 50
        lead = Lead(
            title=long_title,
            date="2024-01-15",
            context="Some context",
            sources=["https://example.com"],
        )

        with (
            patch(
                "services.lead_verification._verify_lead_credibility",
                return_value=False,
            ),
            patch("services.lead_verification.logger") as mock_logger,
        ):
            verify_leads([lead], openai_client=mock_openai_client)

            # Find the call about rejected lead (updated message format)
            discarded_call = None
            for call in mock_logger.info.call_args_list:
                if "rejected" in call[0][0]:
                    discarded_call = call
                    break

            assert discarded_call is not None
            # The rejected message format is: "  ✗ Lead %d/%d rejected - %s: %s"
            # Arguments are: (idx, len(leads), first_words, lead_summary)
            lead_summary = discarded_call[0][4]  # The last argument (lead_summary)
            assert "..." in lead_summary
            assert len(lead_summary.split("...")[0]) <= 50


class TestVerifyLeadCredibility:
    """Test suite for _verify_lead_credibility function."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        return Mock(spec=OpenAIClient)

    @pytest.fixture
    def sample_lead(self):
        """Sample lead for testing."""
        return Lead(
            title="Test news title",
            date="2024-01-15",
            context="Test context",
            sources=["https://reuters.com"],
        )

    def test_verify_lead_passes_all_thresholds(self, mock_openai_client, sample_lead):
        """Test lead that passes all verification thresholds."""
        scores = {
            "source_credibility": MIN_SOURCE_CREDIBILITY_SCORE + 1,
            "context_relevance": MIN_CONTEXT_RELEVANCE_SCORE + 1,
        }

        with patch("services.lead_verification._evaluate_lead_credibility", return_value=scores):
            result = _verify_lead_credibility(sample_lead, mock_openai_client)

            assert result is True

    def test_verify_lead_fails_source_threshold(self, mock_openai_client, sample_lead):
        """Test lead that fails source credibility threshold."""
        scores = {
            "source_credibility": MIN_SOURCE_CREDIBILITY_SCORE - 1,
            "context_relevance": MIN_CONTEXT_RELEVANCE_SCORE + 1,
        }

        with patch("services.lead_verification._evaluate_lead_credibility", return_value=scores):
            result = _verify_lead_credibility(sample_lead, mock_openai_client)

            assert result is False

    def test_verify_lead_fails_context_threshold(self, mock_openai_client, sample_lead):
        """Test lead that fails context relevance threshold."""
        scores = {
            "source_credibility": MIN_SOURCE_CREDIBILITY_SCORE + 1,
            "context_relevance": MIN_CONTEXT_RELEVANCE_SCORE - 1,
        }

        with patch("services.lead_verification._evaluate_lead_credibility", return_value=scores):
            result = _verify_lead_credibility(sample_lead, mock_openai_client)

            assert result is False

    def test_verify_lead_fails_total_threshold(self, mock_openai_client, sample_lead):
        """Test lead that fails total score threshold."""
        # Individual scores pass but total doesn't
        scores = {
            "source_credibility": MIN_SOURCE_CREDIBILITY_SCORE,
            "context_relevance": MIN_TOTAL_SCORE - MIN_SOURCE_CREDIBILITY_SCORE - 1,
        }

        with patch("services.lead_verification._evaluate_lead_credibility", return_value=scores):
            result = _verify_lead_credibility(sample_lead, mock_openai_client)

            assert result is False

    def test_verify_lead_evaluation_error(self, mock_openai_client, sample_lead):
        """Test lead verification when evaluation returns None."""
        with patch("services.lead_verification._evaluate_lead_credibility", return_value=None):
            result = _verify_lead_credibility(sample_lead, mock_openai_client)

            assert result is False

    def test_verify_lead_logs_scores(self, mock_openai_client, sample_lead):
        """Test that verification scores are logged."""
        scores = {"source_credibility": 7.5, "context_relevance": 8.2}

        with (
            patch(
                "services.lead_verification._evaluate_lead_credibility",
                return_value=scores,
            ),
            patch("services.lead_verification.logger") as mock_logger,
        ):
            _verify_lead_credibility(sample_lead, mock_openai_client)

            # Verify that score logging happened
            # (debug logging is in _evaluate_lead_credibility which is mocked)
            # The function logs the score breakdown with info level using emoji
            score_logged = any("📊 Scores:" in str(call) for call in mock_logger.info.call_args_list)
            assert score_logged, "Expected score breakdown to be logged"


class TestEvaluateLeadCredibility:
    """Test suite for _evaluate_lead_credibility function."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        return Mock(spec=OpenAIClient)

    @pytest.fixture
    def sample_lead(self):
        """Sample lead for testing."""
        return Lead(
            title="Test news title",
            date="2024-01-15",
            context="Test context",
            sources=["https://reuters.com", "https://bbc.com"],
        )

    @pytest.fixture
    def sample_lead_no_sources(self):
        """Sample lead without sources."""
        return Lead(title="Test news title", date="2024-01-15", context="Test context", sources=[])

    def test_evaluate_lead_success(self, mock_openai_client, sample_lead):
        """Test successful lead evaluation."""
        response_json = {
            "source_credibility_score": 8.5,
            "context_relevance_score": 7.2,
            "analysis": "Good sources and relevant context",
        }
        mock_openai_client.chat_completion.return_value = json.dumps(response_json)

        result = _evaluate_lead_credibility(sample_lead, mock_openai_client)

        assert result is not None
        assert result["source_credibility"] == 8.5
        assert result["context_relevance"] == 7.2

    def test_evaluate_lead_no_sources(self, mock_openai_client, sample_lead_no_sources):
        """Test evaluation with lead that has no sources."""
        response_json = {
            "source_credibility_score": 2.0,
            "context_relevance_score": 6.0,
            "analysis": "No sources provided",
        }
        mock_openai_client.chat_completion.return_value = json.dumps(response_json)

        result = _evaluate_lead_credibility(sample_lead_no_sources, mock_openai_client)

        assert result is not None
        # Verify the prompt included "No sources provided"
        mock_openai_client.chat_completion.assert_called_once()
        call_args = mock_openai_client.chat_completion.call_args[1]
        assert "No sources provided" in call_args["prompt"]

    def test_evaluate_lead_score_clamping(self, mock_openai_client, sample_lead):
        """Test that scores outside 0-10 range are clamped."""
        response_json = {
            "source_credibility_score": 12.0,  # Above 10
            "context_relevance_score": -2.0,  # Below 0
            "analysis": "Extreme scores",
        }
        mock_openai_client.chat_completion.return_value = json.dumps(response_json)

        result = _evaluate_lead_credibility(sample_lead, mock_openai_client)

        assert result is not None
        assert result["source_credibility"] == 10.0  # Clamped to max
        assert result["context_relevance"] == 0.0  # Clamped to min

    def test_evaluate_lead_json_decode_error(self, mock_openai_client, sample_lead):
        """Test handling of invalid JSON response."""
        mock_openai_client.chat_completion.return_value = "Invalid JSON"

        with patch("services.lead_verification.logger") as mock_logger:
            result = _evaluate_lead_credibility(sample_lead, mock_openai_client)

            assert result is None
            mock_logger.error.assert_called_once()

    def test_evaluate_lead_missing_keys(self, mock_openai_client, sample_lead):
        """Test handling of response missing required keys."""
        response_json = {
            "analysis": "Missing score keys"
            # Missing source_credibility_score and context_relevance_score
        }
        mock_openai_client.chat_completion.return_value = json.dumps(response_json)

        result = _evaluate_lead_credibility(sample_lead, mock_openai_client)

        assert result is not None
        assert result["source_credibility"] == 0.0  # Default value
        assert result["context_relevance"] == 0.0  # Default value

    def test_evaluate_lead_invalid_score_type(self, mock_openai_client, sample_lead):
        """Test handling of non-numeric score values."""
        response_json = {
            "source_credibility_score": "not_a_number",
            "context_relevance_score": 7.0,
            "analysis": "Invalid score type",
        }
        mock_openai_client.chat_completion.return_value = json.dumps(response_json)

        with patch("services.lead_verification.logger") as mock_logger:
            result = _evaluate_lead_credibility(sample_lead, mock_openai_client)

            assert result is None
            mock_logger.error.assert_called_once()

    def test_evaluate_lead_openai_exception(self, mock_openai_client, sample_lead):
        """Test handling of OpenAI client exceptions."""
        mock_openai_client.chat_completion.side_effect = Exception("API Error")

        with patch("services.lead_verification.logger") as mock_logger:
            result = _evaluate_lead_credibility(sample_lead, mock_openai_client)

            assert result is None
            mock_logger.error.assert_called_once()

    def test_evaluate_lead_logs_analysis(self, mock_openai_client, sample_lead):
        """Test that analysis is logged from response."""
        analysis_text = "Detailed verification analysis"
        response_json = {
            "source_credibility_score": 8.0,
            "context_relevance_score": 7.0,
            "analysis": analysis_text,
        }
        mock_openai_client.chat_completion.return_value = json.dumps(response_json)

        with patch("services.lead_verification.logger") as mock_logger:
            _evaluate_lead_credibility(sample_lead, mock_openai_client)

            # Verify analysis was logged
            mock_logger.debug.assert_called_once_with("Verification analysis: %s", analysis_text)

    def test_evaluate_lead_prompt_formatting(self, mock_openai_client, sample_lead):
        """Test that prompt is formatted correctly with lead data."""
        response_json = {
            "source_credibility_score": 8.0,
            "context_relevance_score": 7.0,
            "analysis": "Test analysis",
        }
        mock_openai_client.chat_completion.return_value = json.dumps(response_json)

        _evaluate_lead_credibility(sample_lead, mock_openai_client)

        # Verify the prompt contains lead information
        mock_openai_client.chat_completion.assert_called_once()
        call_args = mock_openai_client.chat_completion.call_args[1]
        prompt = call_args["prompt"]

        assert sample_lead.title in prompt
        assert sample_lead.date in prompt
        assert sample_lead.context in prompt
        assert "https://reuters.com" in prompt
        assert "https://bbc.com" in prompt
