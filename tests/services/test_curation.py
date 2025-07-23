"""Test suite for lead curation service."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead
from services import curate_leads
from services.lead_curation import LeadCurator, LeadEvaluation


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
                discovered_lead=(
                    "Climate Summit 2024: World leaders meet to discuss climate "
                    "change solutions and carbon reduction targets with major "
                    "implications for global policy and economy."
                ),
                report=(
                    "Climate Summit 2024: World leaders from 195 countries "
                    "gathered in Dubai for a critical climate summit to address "
                    "unprecedented global warming challenges. The summit focused "
                    "on binding carbon reduction targets, renewable energy "
                    "transitions, and climate adaptation strategies. Key outcomes "
                    "include a $100 billion climate fund commitment and new "
                    "international frameworks for carbon pricing. The event marks "
                    "a pivotal moment in international climate diplomacy with "
                    "implications for global environmental policy."
                ),
            ),
            Lead(
                discovered_lead=(
                    "Major earthquake in Pacific: A 7.5 magnitude earthquake "
                    "struck the Pacific region causing widespread damage and "
                    "triggering tsunami warnings across multiple countries."
                ),
                report=(
                    "Major earthquake in Pacific: A devastating 7.5 magnitude "
                    "earthquake struck the Pacific Ring of Fire, causing "
                    "widespread destruction across multiple island nations. "
                    "The earthquake triggered tsunami warnings for Japan, "
                    "Philippines, and Indonesia, forcing mass evacuations of "
                    "coastal communities. Emergency response teams are "
                    "coordinating international rescue efforts while assessing "
                    "infrastructure damage estimated in billions of dollars."
                ),
            ),
            Lead(
                discovered_lead=(
                    "Tech breakthrough: Scientists announce revolutionary AI "
                    "system that can predict diseases years before symptoms "
                    "appear, potentially saving millions of lives."
                ),
                report=(
                    "Tech breakthrough in medical AI: Researchers at Stanford "
                    "Medical Center announced a breakthrough artificial "
                    "intelligence system capable of predicting onset of diseases "
                    "including cancer, diabetes, and heart disease up to 5 years "
                    "before clinical symptoms appear. The system achieved 94% "
                    "accuracy in clinical trials involving 100,000 patients. "
                    "This innovation could revolutionize preventive healthcare "
                    "and save millions of lives through early intervention."
                ),
            ),
            Lead(
                discovered_lead=(
                    "Economic crisis deepens: Global markets tumble as inflation "
                    "reaches 40-year high, central banks struggle to respond "
                    "effectively to the growing financial instability."
                ),
                report=(
                    "Economic crisis deepens globally: Financial markets "
                    "experienced massive selloffs as inflation reached 8.9%, "
                    "the highest level in 40 years. The Federal Reserve and "
                    "European Central Bank face difficult decisions between "
                    "aggressive rate hikes and recession risks. Consumer "
                    "confidence plummeted while energy and food prices continue "
                    "surging, creating a perfect storm of economic challenges "
                    "affecting millions worldwide."
                ),
            ),
            Lead(
                discovered_lead=(
                    "Space milestone: First commercial space station successfully "
                    "launches, opening new era of private space exploration and "
                    "research opportunities."
                ),
                report=(
                    "Space milestone achieved: Axiom Space successfully launched "
                    "the first commercially operated space station, marking a "
                    "historic shift from government-led to private sector space "
                    "exploration. The station will conduct scientific research, "
                    "manufacturing experiments, and space tourism operations. "
                    "This achievement opens new frontiers for commercial space "
                    "activities and represents a $2 billion investment in space "
                    "infrastructure."
                ),
            ),
            Lead(
                discovered_lead=("Local sports team wins championship after 50 years, bringing joy to fans and boosting local economy through celebrations."),
                report=(
                    "Local sports championship victory: The city's professional "
                    "baseball team won their first championship in 50 years, "
                    "triggering massive celebrations that boosted the local "
                    "economy by an estimated $50 million. Over 2 million fans "
                    "participated in victory parades while local businesses "
                    "reported record sales. The victory has united the community "
                    "and provided significant economic benefits through tourism "
                    "and merchandise sales."
                ),
            ),
        ]

    def test_curate_leads_empty_input(self, mock_openai_client):
        """Test curate_leads with empty input."""
        result = curate_leads([], openai_client=mock_openai_client)

        assert result == []
        mock_openai_client.chat_completion.assert_not_called()

    def test_curate_leads_basic(self, mock_openai_client, sample_leads):
        """Test basic functionality of curate_leads."""
        # Mock evaluation response
        evaluation_response = json.dumps(
            {
                "evaluations": [
                    {
                        "index": 1,
                        "impact": 9,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 7,
                        "novelty": 6,
                        "conflict": 7,
                        "brief_reasoning": "Major climate policy",
                    },
                    {
                        "index": 2,
                        "impact": 8,
                        "proximity": 7,
                        "prominence": 4,
                        "relevance": 9,
                        "hook": 9,
                        "novelty": 7,
                        "conflict": 3,
                        "brief_reasoning": "Natural disaster",
                    },
                    {
                        "index": 3,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 5,
                        "relevance": 9,
                        "hook": 8,
                        "novelty": 9,
                        "conflict": 4,
                        "brief_reasoning": "Medical breakthrough",
                    },
                    {
                        "index": 4,
                        "impact": 9,
                        "proximity": 9,
                        "prominence": 6,
                        "relevance": 9,
                        "hook": 8,
                        "novelty": 5,
                        "conflict": 8,
                        "brief_reasoning": "Economic crisis",
                    },
                    {
                        "index": 5,
                        "impact": 5,
                        "proximity": 6,
                        "prominence": 6,
                        "relevance": 6,
                        "hook": 7,
                        "novelty": 8,
                        "conflict": 3,
                        "brief_reasoning": "Space milestone",
                    },
                    {
                        "index": 6,
                        "impact": 3,
                        "proximity": 2,
                        "prominence": 3,
                        "relevance": 4,
                        "hook": 5,
                        "novelty": 6,
                        "conflict": 2,
                        "brief_reasoning": "Local sports",
                    },
                ]
            }
        )

        # Mock pairwise response
        pairwise_response = json.dumps(
            {
                "comparisons": [
                    {
                        "pair": "1vs4",
                        "winner": 1,
                        "confidence": "high",
                        "reason": "Climate policy more impactful",
                    }
                ]
            }
        )

        mock_openai_client.chat_completion.side_effect = [
            evaluation_response,
            pairwise_response,
        ]

        result = curate_leads(sample_leads[:5], openai_client=mock_openai_client)

        # Should return some leads (exact number depends on scoring)
        assert len(result) >= 3
        assert len(result) <= 5

        # All returned leads should be from the original set
        for lead in result:
            assert lead in sample_leads[:5]

    def test_curate_leads_formats_correctly(self, mock_openai_client, sample_leads):
        """Test that leads are formatted correctly for AI evaluation."""
        # Mock response
        mock_openai_client.chat_completion.return_value = json.dumps(
            {
                "evaluations": [
                    {
                        "index": 1,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                    }
                ]
            }
        )

        curate_leads(sample_leads, openai_client=mock_openai_client)

        # Verify the method was called
        assert mock_openai_client.chat_completion.called

        # Check that the prompt contains numbered leads
        call_args = mock_openai_client.chat_completion.call_args[0][0]
        assert "1. Climate Summit 2024" in call_args
        assert "2. Major earthquake in Pacific" in call_args

    @patch("services.lead_curation.logger")
    def test_curate_leads_logging(self, mock_logger, mock_openai_client, sample_leads):
        """Test that logging works correctly."""
        # Mock response
        mock_openai_client.chat_completion.return_value = json.dumps(
            {
                "evaluations": [
                    {
                        "index": i + 1,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": f"Lead {i + 1}",
                    }
                    for i in range(6)
                ]
            }
        )

        result = curate_leads(sample_leads, openai_client=mock_openai_client)

        # Check logging calls - updated to match new emoji-based format
        mock_logger.info.assert_any_call("  ⚖️ Analyzing %d leads using multi-criteria evaluation...", 6)
        mock_logger.info.assert_any_call(
            "  ✓ Priority selection complete: %d high-impact leads selected",
            len(result),
        )

    def test_curate_leads_uses_curation_model(self, mock_openai_client, sample_leads):
        """Test that the correct model is used for decision making."""
        from config.curation_config import CURATION_MODEL

        # Mock response
        mock_openai_client.chat_completion.return_value = json.dumps(
            [
                {
                    "index": 1,
                    "impact": 8,
                    "proximity": 8,
                    "prominence": 8,
                    "relevance": 8,
                    "hook": 8,
                    "novelty": 8,
                    "conflict": 8,
                }
            ]
        )

        curate_leads(sample_leads, openai_client=mock_openai_client)

        # Verify model parameter was used in at least one call
        calls = mock_openai_client.chat_completion.call_args_list
        assert any(call.kwargs.get("model") == CURATION_MODEL for call in calls if call.kwargs)

    def test_curate_leads_fallback_behavior(self, mock_openai_client, sample_leads):
        """Test fallback behavior when evaluation fails."""
        # Mock invalid JSON response
        mock_openai_client.chat_completion.return_value = "Invalid JSON response"

        result = curate_leads(sample_leads, openai_client=mock_openai_client)

        # Should still return minimum number of leads due to fallback scoring
        assert len(result) >= 3
        assert all(lead in sample_leads for lead in result)


class TestLeadCurator:
    """Test suite for LeadCurator class internals."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        return Mock()

    @pytest.fixture
    def sample_leads(self):
        """Sample leads for testing."""
        return [
            Lead(
                discovered_lead="Climate Summit 2024: World leaders meet to discuss climate "
                "change solutions and carbon reduction targets with major implications "
                "for global policy and economy.",
            ),
            Lead(
                discovered_lead="Major earthquake in Pacific: A 7.5 magnitude earthquake "
                "struck the Pacific region causing widespread damage and triggering "
                "tsunami warnings across multiple countries.",
            ),
            Lead(
                discovered_lead="Tech breakthrough: Scientists announce revolutionary AI "
                "system that can predict diseases years before symptoms appear, "
                "potentially saving millions of lives.",
            ),
            Lead(
                discovered_lead="Economic crisis deepens: Global markets tumble as inflation "
                "reaches 40-year high, central banks struggle to respond effectively "
                "to the growing financial instability.",
            ),
            Lead(
                discovered_lead="Space milestone: First commercial space station successfully "
                "launches, opening new era of private space exploration and research "
                "opportunities.",
            ),
            Lead(
                discovered_lead="Local sports team wins championship after 50 years, bringing joy to fans and boosting local economy through celebrations.",
            ),
        ]

    def test_curator_initialization(self, mock_openai_client):
        """Test curator initialization."""
        curator = LeadCurator(mock_openai_client)

        assert curator.openai_client == mock_openai_client
        assert sum(curator.CRITERIA_WEIGHTS.values()) == 1.0  # Weights sum to 1

    def test_curator_empty_input(self, mock_openai_client):
        """Test curating empty lead list."""
        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads([])

        assert result == []
        mock_openai_client.chat_completion.assert_not_called()

    def test_multi_criteria_evaluation(self, mock_openai_client, sample_leads):
        """Test multi-criteria evaluation step."""
        # Mock response for criteria evaluation
        evaluation_response = json.dumps(
            {
                "evaluations": [
                    {
                        "index": 1,
                        "impact": 9,  # High global impact
                        "proximity": 9,  # Global relevance
                        "prominence": 8,  # World leaders
                        "relevance": 8,  # Hot topic
                        "hook": 7,  # Strong headline potential
                        "novelty": 6,  # Somewhat expected
                        "conflict": 7,  # Political disagreements
                        "brief_reasoning": ("Major global climate policy with world leaders"),
                    },
                    {
                        "index": 2,
                        "impact": 8,  # Affects many people
                        "proximity": 7,  # Regional but significant
                        "prominence": 4,  # No celebrities
                        "relevance": 9,  # Disasters always relevant
                        "hook": 9,  # Very attention-grabbing
                        "novelty": 7,  # Earthquakes are shocking
                        "conflict": 3,  # Natural disaster, no conflict
                        "brief_reasoning": "Major natural disaster affecting thousands",
                    },
                    {
                        "index": 3,
                        "impact": 8,  # Potential to help millions
                        "proximity": 8,  # Global healthcare impact
                        "prominence": 5,  # Scientists not celebrities
                        "relevance": 9,  # Health is universal concern
                        "hook": 8,  # Breakthrough grabs attention
                        "novelty": 9,  # Revolutionary technology
                        "conflict": 4,  # Some ethical debates
                        "brief_reasoning": "Revolutionary medical breakthrough",
                    },
                    {
                        "index": 4,
                        "impact": 9,  # Global economic impact
                        "proximity": 9,  # Affects everyone
                        "prominence": 6,  # Central banks mentioned
                        "relevance": 9,  # Money matters to all
                        "hook": 8,  # Crisis headlines work
                        "novelty": 5,  # Economic crises happen
                        "conflict": 8,  # Policy disagreements
                        "brief_reasoning": "Global economic crisis",
                    },
                    {
                        "index": 5,
                        "impact": 5,  # Limited immediate impact
                        "proximity": 6,  # Space interests some
                        "prominence": 6,  # Known companies
                        "relevance": 6,  # Niche interest
                        "hook": 7,  # Space is cool
                        "novelty": 8,  # First of its kind
                        "conflict": 3,  # No controversy
                        "brief_reasoning": "Space exploration milestone",
                    },
                    {
                        "index": 6,
                        "impact": 3,  # Local impact only
                        "proximity": 2,  # Very local story
                        "prominence": 3,  # Unknown players
                        "relevance": 4,  # Limited audience
                        "hook": 5,  # Feel-good but limited
                        "novelty": 6,  # 50 years is notable
                        "conflict": 2,  # Sports victory, no conflict
                        "brief_reasoning": "Local sports victory",
                    },
                ]
            }
        )

        mock_openai_client.chat_completion.return_value = evaluation_response

        curator = LeadCurator(mock_openai_client)
        evaluations = curator._evaluate_all_criteria(sample_leads)

        assert len(evaluations) == 6

        # Check weighted scores calculation
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
                criteria_scores={
                    "impact": 8,
                    "proximity": 8,
                    "prominence": 8,
                    "relevance": 8,
                    "hook": 8,
                    "novelty": 8,
                    "conflict": 8,
                },
                weighted_score=8.0,
            ),
            LeadEvaluation(
                lead=sample_leads[1],
                criteria_scores={
                    "impact": 8,
                    "proximity": 7,
                    "prominence": 7,
                    "relevance": 9,
                    "hook": 8,
                    "novelty": 7,
                    "conflict": 8,
                },
                weighted_score=7.8,
            ),
            LeadEvaluation(
                lead=sample_leads[2],
                criteria_scores={
                    "impact": 8,
                    "proximity": 8,
                    "prominence": 6,
                    "relevance": 8,
                    "hook": 8,
                    "novelty": 9,
                    "conflict": 7,
                },
                weighted_score=7.9,
            ),
        ]

        # Mock pairwise comparison response
        pairwise_response = json.dumps(
            {
                "comparisons": [
                    {
                        "pair": "1vs2",
                        "winner": 1,
                        "confidence": "high",
                        "reason": "Climate more impactful",
                    },
                    {
                        "pair": "1vs3",
                        "winner": 1,
                        "confidence": "medium",
                        "reason": "Climate affects more people",
                    },
                    {
                        "pair": "2vs3",
                        "winner": 3,
                        "confidence": "high",
                        "reason": "Tech breakthrough more novel",
                    },
                ]
            }
        )

        mock_openai_client.chat_completion.return_value = pairwise_response

        curator = LeadCurator(mock_openai_client)
        curator._compare_group_pairwise(evaluations)

        # Check pairwise wins
        assert evaluations[0].pairwise_wins == 2  # Won both comparisons
        assert evaluations[1].pairwise_wins == 0  # Lost both
        assert evaluations[2].pairwise_wins == 1  # Won against 2

    def test_final_ranking_calculation(self, mock_openai_client, sample_leads):
        """Test final ranking calculation."""
        evaluations = [
            LeadEvaluation(
                lead=Lead(discovered_lead="Lead 1"),
                criteria_scores={},
                weighted_score=8.0,
                pairwise_wins=2,
            ),
            LeadEvaluation(
                lead=Lead(discovered_lead="Lead 2"),
                criteria_scores={},
                weighted_score=7.5,
                pairwise_wins=1,
            ),
            LeadEvaluation(
                lead=Lead(discovered_lead="Lead 3"),
                criteria_scores={},
                weighted_score=7.8,
                pairwise_wins=0,
            ),
        ]

        curator = LeadCurator(mock_openai_client)
        ranked = curator._compute_final_ranking(evaluations)

        # Lead 1 should rank first: 0.7 * 8.0 + 0.3 * 10 = 8.6
        # Lead 2 should rank second: 0.7 * 7.5 + 0.3 * 5 = 6.75
        # Lead 3 should rank third: 0.7 * 7.8 + 0.3 * 0 = 5.46

        assert ranked[0].lead.discovered_lead == "Lead 1"
        assert ranked[1].lead.discovered_lead == "Lead 2"
        assert ranked[2].lead.discovered_lead == "Lead 3"

    def test_top_selection(self, mock_openai_client):
        """Test top lead selection."""
        curator = LeadCurator(mock_openai_client)

        # Create ranked evaluations
        evaluations = [
            LeadEvaluation(
                lead=Lead(discovered_lead=f"Lead {i}"),
                criteria_scores={},
                weighted_score=10 - i,
                final_rank=10 - i,
            )
            for i in range(8)
        ]

        selected = curator._select_top_leads(evaluations)

        # Should select top MAX_LEADS_TO_SELECT leads
        assert len(selected) == curator.MAX_LEADS_TO_SELECT

        # Should be the highest ranked ones
        for i, eval in enumerate(selected):
            assert eval.lead.discovered_lead == f"Lead {i}"

    def test_full_pipeline_integration(self, mock_openai_client, sample_leads):
        """Test the complete curation pipeline."""
        # Mock evaluation response
        evaluation_response = json.dumps(
            [
                {
                    "index": i + 1,
                    "impact": 9 - i,
                    "proximity": 8,
                    "prominence": 7,
                    "relevance": 8,
                    "hook": 7,
                    "novelty": 6,
                    "conflict": 5,
                    "brief_reasoning": f"Lead {i + 1}",
                }
                for i in range(len(sample_leads))
            ]
        )

        # Mock pairwise response
        pairwise_response = json.dumps(
            [
                {"pair": "1vs2", "winner": 1, "confidence": "high"},
                {"pair": "2vs3", "winner": 2, "confidence": "medium"},
            ]
        )

        # Create a cyclical response to handle any number of pairwise calls
        pairwise_responses = [pairwise_response] * 10
        mock_openai_client.chat_completion.side_effect = [evaluation_response] + pairwise_responses

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads(sample_leads)

        # Should return between MIN and MAX leads
        assert curator.MIN_LEADS_TO_SELECT <= len(result) <= curator.MAX_LEADS_TO_SELECT

        # Verify high-scoring leads are included
        result_titles = [lead.discovered_lead for lead in result]
        assert any("Climate Summit" in title for title in result_titles)

    def test_fallback_behavior(self, mock_openai_client, sample_leads):
        """Test fallback when all leads score below threshold."""
        # Mock very low scores
        low_score_response = json.dumps(
            [
                {
                    "index": i + 1,
                    "impact": 3,
                    "proximity": 2,
                    "prominence": 3,
                    "relevance": 2,
                    "hook": 4,
                    "novelty": 3,
                    "conflict": 2,
                    "brief_reasoning": f"Low impact lead {i + 1}",
                }
                for i in range(len(sample_leads))
            ]
        )

        mock_openai_client.chat_completion.return_value = low_score_response

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads(sample_leads)

        # Should still return minimum number of leads
        assert len(result) == curator.MIN_LEADS_TO_SELECT

    @patch("services.lead_curation.logger")
    def test_curator_logging(self, mock_logger, mock_openai_client, sample_leads):
        """Test that appropriate logging occurs."""
        # Mock simple response
        mock_openai_client.chat_completion.return_value = json.dumps(
            [
                {
                    "index": 1,
                    "impact": 8,
                    "proximity": 8,
                    "prominence": 8,
                    "relevance": 8,
                    "hook": 8,
                    "novelty": 8,
                    "conflict": 8,
                }
            ]
        )

        curator = LeadCurator(mock_openai_client)
        curator.curate_leads(sample_leads[:1])

        # Verify logging calls - updated to match new emoji-based format
        mock_logger.info.assert_any_call("  ⚖️ Analyzing %d leads using multi-criteria evaluation...", 1)
        mock_logger.info.assert_any_call("  ✓ Priority selection complete: %d high-impact leads selected", 1)


class TestLeadCurationEdgeCases:
    """Test suite for lead curation edge cases and error handling."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        return Mock()

    @pytest.fixture
    def sample_lead(self):
        """Single sample lead for testing."""
        return Lead(
            discovered_lead="Test lead for edge case testing",
            report="Test context for edge case scenarios",
        )

    @patch("services.lead_curation.logger")
    def test_json_parsing_dict_without_evaluations(self, mock_logger, mock_openai_client, sample_lead):
        """Test JSON parsing when response is dict without 'evaluations' key
        but contains a list."""
        # Response is a dict with a list value, not in 'evaluations' key
        mock_response = {
            "data": [
                {
                    "index": 1,
                    "impact": 8,
                    "proximity": 8,
                    "prominence": 8,
                    "relevance": 8,
                    "hook": 8,
                    "novelty": 8,
                    "conflict": 8,
                }
            ],
            "metadata": "some info",
        }
        mock_openai_client.chat_completion.return_value = json.dumps(mock_response)

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads([sample_lead])

        assert len(result) == 1

    @patch("services.lead_curation.logger")
    def test_json_parsing_dict_no_array_found(self, mock_logger, mock_openai_client, sample_lead):
        """Test JSON parsing when response is dict with no list values."""
        # Response is a dict with no list values
        mock_response = {"message": "No evaluations available", "status": "error"}
        mock_openai_client.chat_completion.return_value = json.dumps(mock_response)

        curator = LeadCurator(mock_openai_client)

        # Should fall back to original leads when parsing fails
        result = curator.curate_leads([sample_lead])

        # Should return the original leads when evaluation fails
        assert len(result) == 1
        mock_logger.error.assert_called()

    @patch("services.lead_curation.logger")
    def test_json_parsing_invalid_type(self, mock_logger, mock_openai_client, sample_lead):
        """Test JSON parsing when response is neither list nor dict."""
        # Response is a string, not list or dict
        mock_openai_client.chat_completion.return_value = '"Invalid response type"'

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads([sample_lead])

        # Should return original leads when parsing fails
        assert len(result) == 1
        mock_logger.error.assert_called()

    @patch("services.lead_curation.logger")
    def test_missing_criteria_scores_warning(self, mock_logger, mock_openai_client, sample_lead):
        """Test warning is logged when criteria scores are missing from evaluation."""
        # Response missing some criteria (e.g., missing 'novelty' and 'conflict')
        mock_response = [
            {
                "index": 1,
                "impact": 8,
                "proximity": 7,
                "prominence": 6,
                "relevance": 8,
                "hook": 7,
                # Missing 'novelty' and 'conflict'
            }
        ]
        mock_openai_client.chat_completion.return_value = json.dumps(mock_response)

        curator = LeadCurator(mock_openai_client)
        curator.curate_leads([sample_lead])

        # Should log warning about missing criteria
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0]
        assert "FALLBACK" in warning_call[0]
        assert "missing criteria scores" in warning_call[0]

    def test_pairwise_comparison_enabled(self, mock_openai_client):
        """Test pairwise comparison is triggered when group size meets minimum."""
        # Create enough leads to trigger pairwise comparison
        leads = [
            Lead(discovered_lead=f"Test lead {i + 1}", report=f"Context for lead {i + 1}")
            for i in range(6)  # More than MIN_GROUP_SIZE_FOR_PAIRWISE (usually 4-5)
        ]

        # Mock response with similar scores to trigger grouping
        mock_response = [
            {
                "index": i + 1,
                "impact": 8,  # All have similar scores
                "proximity": 8,
                "prominence": 8,
                "relevance": 8,
                "hook": 8,
                "novelty": 8,
                "conflict": 8,
            }
            for i in range(6)
        ]

        mock_openai_client.chat_completion.return_value = json.dumps(mock_response)

        curator = LeadCurator(mock_openai_client)

        # Mock the _compare_group_pairwise method to verify it's called
        with patch.object(curator, "_compare_group_pairwise") as mock_pairwise:
            curator.curate_leads(leads)

            # Should call pairwise comparison for the group
            mock_pairwise.assert_called()

    def test_minimum_leads_selection_fallback(self, mock_openai_client):
        """Test fallback to minimum leads selection when not enough leads pass
        thresholds."""
        # Create more leads than minimum required
        leads = [Lead(discovered_lead=f"Test lead {i + 1}", report=f"Context for lead {i + 1}") for i in range(6)]

        # Mock response with low scores that won't pass normal selection
        mock_response = [
            {
                "index": i + 1,
                "impact": 3,  # Low scores
                "proximity": 3,
                "prominence": 3,
                "relevance": 3,
                "hook": 3,
                "novelty": 3,
                "conflict": 3,
            }
            for i in range(6)
        ]

        mock_openai_client.chat_completion.return_value = json.dumps(mock_response)

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads(leads)

        # Should fall back to selecting minimum number of leads
        assert len(result) == curator.MIN_LEADS_TO_SELECT

    def test_pairwise_comparison_skipped_small_group(self, mock_openai_client):
        """Test pairwise comparison is skipped when group is too small."""
        # Create few leads - less than MIN_GROUP_SIZE_FOR_PAIRWISE
        leads = [
            Lead(discovered_lead=f"Test lead {i + 1}", report=f"Context for lead {i + 1}")
            for i in range(2)  # Less than minimum group size
        ]

        mock_response = [
            {
                "index": i + 1,
                "impact": 8,
                "proximity": 8,
                "prominence": 8,
                "relevance": 8,
                "hook": 8,
                "novelty": 8,
                "conflict": 8,
            }
            for i in range(2)
        ]

        mock_openai_client.chat_completion.return_value = json.dumps(mock_response)

        curator = LeadCurator(mock_openai_client)

        # Mock the _compare_group_pairwise method to verify it's not called
        with patch.object(curator, "_compare_group_pairwise") as mock_pairwise:
            curator.curate_leads(leads)

            # Should not call pairwise comparison for small group
            mock_pairwise.assert_not_called()

    @patch("services.lead_curation.logger")
    def test_json_decode_error_handling(self, mock_logger, mock_openai_client, sample_lead):
        """Test handling of invalid JSON response."""
        # Return invalid JSON
        mock_openai_client.chat_completion.return_value = "Invalid JSON {"

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads([sample_lead])

        # Should log error and return original leads
        mock_logger.error.assert_called()
        assert len(result) == 1
