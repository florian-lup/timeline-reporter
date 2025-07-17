"""Test suite for hybrid lead curation system."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead
from services.hybrid_curator import HybridLeadCurator, LeadEvaluation


class TestHybridCurator:
    """Test suite for hybrid lead curation."""

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
                "change solutions and carbon reduction targets with major implications "
                "for global policy and economy.",
            ),
            Lead(
                context="Major earthquake in Pacific: A 7.5 magnitude earthquake "
                "struck the Pacific region causing widespread damage and triggering "
                "tsunami warnings across multiple countries.",
            ),
            Lead(
                context="Tech breakthrough: Scientists announce revolutionary AI "
                "system that can predict diseases years before symptoms appear, "
                "potentially saving millions of lives.",
            ),
            Lead(
                context="Economic crisis deepens: Global markets tumble as inflation "
                "reaches 40-year high, central banks struggle to respond effectively "
                "to the growing financial instability.",
            ),
            Lead(
                context="Space milestone: First commercial space station successfully "
                "launches, opening new era of private space exploration and research "
                "opportunities.",
            ),
            Lead(
                context="Local sports team wins championship after 50 years, bringing "
                "joy to fans and boosting local economy through celebrations.",
            ),
        ]

    def test_hybrid_curator_initialization(self, mock_openai_client):
        """Test hybrid curator initialization."""
        curator = HybridLeadCurator(mock_openai_client)

        assert curator.openai_client == mock_openai_client
        assert sum(curator.CRITERIA_WEIGHTS.values()) == 1.0  # Weights sum to 1

    def test_curate_leads_empty_input(self, mock_openai_client):
        """Test curating empty lead list."""
        curator = HybridLeadCurator(mock_openai_client)
        result = curator.curate_leads([])

        assert result == []
        mock_openai_client.chat_completion.assert_not_called()

    def test_multi_criteria_evaluation(self, mock_openai_client, sample_leads):
        """Test multi-criteria evaluation step."""
        # Mock response for criteria evaluation
        evaluation_response = json.dumps([
            {
                "index": 1,
                "impact": 9,              # High global impact
                "proximity": 9,           # Global relevance
                "prominence": 8,          # World leaders
                "relevance": 8,           # Hot topic
                "hook": 7,               # Strong headline potential
                "novelty": 6,            # Somewhat expected
                "conflict": 7,           # Political disagreements
                "brief_reasoning": "Major global climate policy with world leaders"
            },
            {
                "index": 2,
                "impact": 8,              # Affects many people
                "proximity": 7,           # Regional but significant
                "prominence": 4,          # No celebrities
                "relevance": 9,           # Disasters always relevant
                "hook": 9,               # Very attention-grabbing
                "novelty": 7,            # Earthquakes are shocking
                "conflict": 3,           # Natural disaster, no conflict
                "brief_reasoning": "Major natural disaster affecting thousands"
            },
            {
                "index": 3,
                "impact": 8,              # Potential to help millions
                "proximity": 8,           # Global healthcare impact
                "prominence": 5,          # Scientists not celebrities
                "relevance": 9,           # Health is universal concern
                "hook": 8,               # Breakthrough grabs attention
                "novelty": 9,            # Revolutionary technology
                "conflict": 4,           # Some ethical debates
                "brief_reasoning": "Revolutionary medical breakthrough"
            },
            {
                "index": 4,
                "impact": 9,              # Global economic impact
                "proximity": 9,           # Affects everyone
                "prominence": 6,          # Central banks mentioned
                "relevance": 9,           # Money matters to all
                "hook": 8,               # Crisis headlines work
                "novelty": 5,            # Economic crises happen
                "conflict": 8,           # Policy disagreements
                "brief_reasoning": "Global economic crisis"
            },
            {
                "index": 5,
                "impact": 5,              # Limited immediate impact
                "proximity": 6,           # Space interests some
                "prominence": 6,          # Known companies
                "relevance": 6,           # Niche interest
                "hook": 7,               # Space is cool
                "novelty": 8,            # First of its kind
                "conflict": 3,           # No controversy
                "brief_reasoning": "Space exploration milestone"
            },
            {
                "index": 6,
                "impact": 3,              # Local impact only
                "proximity": 2,           # Very local story
                "prominence": 3,          # Unknown players
                "relevance": 4,           # Limited audience
                "hook": 5,               # Feel-good but limited
                "novelty": 6,            # 50 years is notable
                "conflict": 2,           # Sports victory, no conflict
                "brief_reasoning": "Local sports victory"
            }
        ])

        mock_openai_client.chat_completion.return_value = evaluation_response

        curator = HybridLeadCurator(mock_openai_client)
        evaluations = curator._evaluate_all_criteria(sample_leads)

        assert len(evaluations) == 6

        # Check weighted scores calculation with new weights
        # Climate summit: (9*0.20 + 9*0.15 + 8*0.15 + 8*0.15 + 7*0.15 +
        #                 6*0.10 + 7*0.10) = 7.9
        assert abs(evaluations[0].weighted_score - 7.9) < 0.01

        # Sports (should be lowest): (3*0.20 + 2*0.15 + 3*0.15 + 4*0.15 +
        #                            5*0.15 + 6*0.10 + 2*0.10) = 3.5
        assert abs(evaluations[5].weighted_score - 3.5) < 0.01

    def test_pairwise_comparison(self, mock_openai_client, sample_leads):
        """Test pairwise comparison functionality."""
        # Create evaluations with similar scores
        evaluations = [
            LeadEvaluation(
                lead=sample_leads[0],
                criteria_scores={"impact": 8, "proximity": 8, "prominence": 8,
                               "relevance": 8, "hook": 8, "novelty": 8, "conflict": 8},
                weighted_score=8.0
            ),
            LeadEvaluation(
                lead=sample_leads[1],
                criteria_scores={"impact": 8, "proximity": 7, "prominence": 7,
                               "relevance": 9, "hook": 8, "novelty": 7, "conflict": 8},
                weighted_score=7.8
            ),
            LeadEvaluation(
                lead=sample_leads[2],
                criteria_scores={"impact": 8, "proximity": 8, "prominence": 6,
                               "relevance": 8, "hook": 8, "novelty": 9, "conflict": 7},
                weighted_score=7.9
            )
        ]

        # Mock pairwise comparison response
        pairwise_response = json.dumps([
            {"pair": "1vs2", "winner": 1, "confidence": "high",
             "reason": "Climate more impactful"},
            {"pair": "1vs3", "winner": 1, "confidence": "medium",
             "reason": "Climate affects more people"},
            {"pair": "2vs3", "winner": 3, "confidence": "high",
             "reason": "Tech breakthrough more novel"}
        ])

        mock_openai_client.chat_completion.return_value = pairwise_response

        curator = HybridLeadCurator(mock_openai_client)
        curator._compare_group_pairwise(evaluations)

        # Check pairwise wins
        assert evaluations[0].pairwise_wins == 2  # Won both comparisons
        assert evaluations[1].pairwise_wins == 0  # Lost both
        assert evaluations[2].pairwise_wins == 1  # Won against 2

    def test_final_ranking_computation(self, mock_openai_client):
        """Test final ranking calculation."""
        evaluations = [
            LeadEvaluation(
                lead=Lead(context="Lead 1"),
                criteria_scores={},
                weighted_score=8.0,
                pairwise_wins=2
            ),
            LeadEvaluation(
                lead=Lead(context="Lead 2"),
                criteria_scores={},
                weighted_score=7.5,
                pairwise_wins=1
            ),
            LeadEvaluation(
                lead=Lead(context="Lead 3"),
                criteria_scores={},
                weighted_score=7.8,
                pairwise_wins=0
            )
        ]

        curator = HybridLeadCurator(mock_openai_client)
        ranked = curator._compute_final_ranking(evaluations)

        # Lead 1 should rank first: 0.7 * 8.0 + 0.3 * 10 = 8.6
        # Lead 2 should rank second: 0.7 * 7.5 + 0.3 * 5 = 6.75
        # Lead 3 should rank third: 0.7 * 7.8 + 0.3 * 0 = 5.46

        assert ranked[0].lead.context == "Lead 1"
        assert ranked[1].lead.context == "Lead 2"
        assert ranked[2].lead.context == "Lead 3"

    def test_top_selection(self, mock_openai_client):
        """Test top lead selection without diversity."""
        curator = HybridLeadCurator(mock_openai_client)

        # Create ranked evaluations
        evaluations = [
            LeadEvaluation(lead=Lead(context=f"Lead {i}"), criteria_scores={},
                         weighted_score=10-i, final_rank=10-i)
            for i in range(8)
        ]

        selected = curator._select_top_leads(evaluations)

        # Should select top MAX_LEADS_TO_SELECT leads
        assert len(selected) == curator.MAX_LEADS_TO_SELECT

        # Should be the highest ranked ones
        for i, eval in enumerate(selected):
            assert eval.lead.context == f"Lead {i}"

    def test_full_pipeline_integration(self, mock_openai_client, sample_leads):
        """Test the complete hybrid curation pipeline."""
        # Mock evaluation response with new criteria
        evaluation_response = json.dumps([
            {"index": i + 1, "impact": 9 - i, "proximity": 8,
             "prominence": 7, "relevance": 8, "hook": 7,
             "novelty": 6, "conflict": 5,
             "brief_reasoning": f"Lead {i + 1}"}
            for i in range(len(sample_leads))
        ])

        # Mock pairwise response
        pairwise_response = json.dumps([
            {"pair": "1vs2", "winner": 1, "confidence": "high"},
            {"pair": "2vs3", "winner": 2, "confidence": "medium"}
        ])

        # Create a cyclical response to handle any number of pairwise calls
        pairwise_responses = [pairwise_response] * 10  # Provide enough responses
        mock_openai_client.chat_completion.side_effect = (
            [evaluation_response] + pairwise_responses
        )

        curator = HybridLeadCurator(mock_openai_client)
        result = curator.curate_leads(sample_leads)

        # Should return between MIN and MAX leads
        assert curator.MIN_LEADS_TO_SELECT <= len(result) <= curator.MAX_LEADS_TO_SELECT

        # Verify high-scoring leads are included
        result_contexts = [lead.context for lead in result]
        assert any("Climate Summit" in ctx for ctx in result_contexts)

    def test_fallback_behavior(self, mock_openai_client, sample_leads):
        """Test fallback when all leads score below threshold."""
        # Mock very low scores
        low_score_response = json.dumps([
            {"index": i + 1, "impact": 3, "proximity": 2,
             "prominence": 3, "relevance": 2, "hook": 4,
             "novelty": 3, "conflict": 2,
             "brief_reasoning": f"Low impact lead {i + 1}"}
            for i in range(len(sample_leads))
        ])

        mock_openai_client.chat_completion.return_value = low_score_response

        curator = HybridLeadCurator(mock_openai_client)
        result = curator.curate_leads(sample_leads)

        # Should still return minimum number of leads
        assert len(result) == curator.MIN_LEADS_TO_SELECT

    @patch("services.hybrid_curator.logger")
    def test_logging(self, mock_logger, mock_openai_client, sample_leads):
        """Test that appropriate logging occurs."""
        # Mock simple response with new criteria
        mock_openai_client.chat_completion.return_value = json.dumps([
            {"index": 1, "impact": 8, "proximity": 8,
             "prominence": 8, "relevance": 8, "hook": 8,
             "novelty": 8, "conflict": 8}
        ])

        curator = HybridLeadCurator(mock_openai_client)
        curator.curate_leads(sample_leads[:1])

        # Verify logging calls
        mock_logger.info.assert_any_call("Starting hybrid curation for %d leads", 1)
        mock_logger.info.assert_any_call("Selected %d leads through hybrid curation", 1)
