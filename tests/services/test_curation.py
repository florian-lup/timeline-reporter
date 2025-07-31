"""Test suite for lead curation service."""

import json
from unittest.mock import Mock, patch

import pytest

from config.curation_config import MAX_LEADS
from models import Lead
from services import curate_leads
from services.lead_curation import LeadCurator
from models import LeadEvaluation


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
                        "index": i + 1,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": f"Test lead evaluation {i + 1}",
                    }
                    for i in range(6)
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
                        "brief_reasoning": f"Test lead evaluation {i + 1}",
                    }
                    for i in range(6)
                ]
            }
        )

        curate_leads(sample_leads, openai_client=mock_openai_client)

        # Verify model parameter was used in at least one call
        calls = mock_openai_client.chat_completion.call_args_list
        assert any(call.kwargs.get("model") == CURATION_MODEL for call in calls if call.kwargs)

    def test_curate_leads_fallback_behavior(self, mock_openai_client, sample_leads):
        """Test that invalid JSON response raises appropriate error."""
        # Mock invalid JSON response
        mock_openai_client.chat_completion.return_value = "Invalid JSON response"

        with pytest.raises(json.JSONDecodeError):
            curate_leads(sample_leads, openai_client=mock_openai_client)


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
        from config.curation_config import CRITERIA_WEIGHTS
        
        curator = LeadCurator(mock_openai_client)

        assert curator.openai_client == mock_openai_client
        assert len(CRITERIA_WEIGHTS) == 7  # All criteria are defined
        assert all(weight > 0 for weight in CRITERIA_WEIGHTS.values())  # All weights are positive

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
        # Climate summit - weight formula has changed, check expected value is around 8.25
        assert abs(evaluations[0].weighted_score - 8.25) < 0.01

        # Sports (should be lowest): weight formula has changed, check expected value is around 3.25
        assert abs(evaluations[5].weighted_score - 3.25) < 0.01

    def test_final_ranking_calculation(self, mock_openai_client, sample_leads):
        """Test final ranking calculation."""
        evaluations = [
            LeadEvaluation(
                lead=Lead(discovered_lead="Lead 1"),
                criteria_scores={},
                weighted_score=8.0,
            ),
            LeadEvaluation(
                lead=Lead(discovered_lead="Lead 2"),
                criteria_scores={},
                weighted_score=7.5,
            ),
            LeadEvaluation(
                lead=Lead(discovered_lead="Lead 3"),
                criteria_scores={},
                weighted_score=7.8,
            ),
        ]

        curator = LeadCurator(mock_openai_client)
        ranked = curator._compute_final_ranking(evaluations)

        # Lead 1 should rank first: 8.0
        # Lead 3 should rank second: 7.8  
        # Lead 2 should rank third: 7.5

        assert ranked[0].lead.discovered_lead == "Lead 1"
        assert ranked[1].lead.discovered_lead == "Lead 3"
        assert ranked[2].lead.discovered_lead == "Lead 2"

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

        # Should select top MAX_LEADS leads
        assert len(selected) == MAX_LEADS

        # Should be the highest ranked ones
        for i, eval in enumerate(selected):
            assert eval.lead.discovered_lead == f"Lead {i}"

    def test_full_pipeline_integration(self, mock_openai_client, sample_leads):
        """Test the complete curation pipeline."""
        # Mock evaluation response
        evaluation_response = json.dumps({
            "evaluations": [
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
        })

        mock_openai_client.chat_completion.return_value = evaluation_response

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads(sample_leads)

        # Should return between MIN and MAX leads
        assert len(result) >= 3
        assert len(result) <= MAX_LEADS

        # Verify high-scoring leads are included
        result_titles = [lead.discovered_lead for lead in result]
        assert any("Climate Summit" in title for title in result_titles)

    def test_fallback_behavior(self, mock_openai_client, sample_leads):
        """Test behavior when all leads score below threshold."""
        # Mock very low scores
        low_score_response = json.dumps(
            {
                "evaluations": [
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
            }
        )

        mock_openai_client.chat_completion.return_value = low_score_response

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads(sample_leads)

        # Should return empty list when no leads pass threshold
        assert len(result) == 0

    @patch("services.lead_curation.logger")
    def test_curator_logging(self, mock_logger, mock_openai_client, sample_leads):
        """Test that appropriate logging occurs."""
        # Mock simple response
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
                        "brief_reasoning": "Test reasoning",
                    }
                ]
            }
        )

        curator = LeadCurator(mock_openai_client)
        curator.curate_leads(sample_leads[:1])

        # Verify logging calls - updated to match new emoji-based format
        mock_logger.info.assert_any_call("  ⚖️ Analyzing %d leads using multi-criteria evaluation...", 1)
        mock_logger.info.assert_any_call("  ✓ Priority selection complete: %d high-impact leads selected", 1)


class TestLeadCurationEdgeCases:
    """Test suite for edge cases with structured output."""

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

    def test_json_decode_error_handling(self, mock_openai_client, sample_lead):
        """Test handling of invalid JSON response."""
        # Return invalid JSON
        mock_openai_client.chat_completion.return_value = "Invalid JSON {"

        curator = LeadCurator(mock_openai_client)
        
        with pytest.raises(json.JSONDecodeError):
            curator.curate_leads([sample_lead])

    def test_low_scoring_leads_returns_empty(self, mock_openai_client):
        """Test that low scoring leads return empty list when below threshold."""
        # Create leads that will score very low
        leads = [Lead(discovered_lead=f"Low priority lead {i}", report="") for i in range(6)]

        # Mock response with very low scores (below MIN_SCORE threshold)
        mock_response = {
            "evaluations": [
                {
                    "index": i + 1,
                    "impact": 1,
                    "proximity": 1,
                    "prominence": 1,
                    "relevance": 1,
                    "hook": 1,
                    "novelty": 1,
                    "conflict": 1,
                    "brief_reasoning": f"Low scoring lead {i + 1}",
                }
                for i in range(6)
            ]
        }
        mock_openai_client.chat_completion.return_value = json.dumps(mock_response)

        curator = LeadCurator(mock_openai_client)
        result = curator.curate_leads(leads)

        # Should return empty list when no leads meet minimum threshold
        assert len(result) == 0
