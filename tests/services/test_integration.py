"""Integration tests for services pipeline."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead, Story
from services import (
    curate_leads,
    deduplicate_leads,
    discover_leads,
    persist_stories,
    research_story,
)


@pytest.mark.integration
class TestServicesIntegration:
    """Integration tests showing how services work together."""

    @pytest.fixture
    def test_discovery_instructions(self):
        """Test-specific discovery instructions with fixed date."""
        return (
            "Identify significant news about climate, environment and natural "
            "disasters, and major geopolitical leads from today 2024-01-15. "
            "Follow these guidelines: Focus on current, breaking news; Include "
            "global conflicts, policy changes, natural disasters, and tech "
            "Return your findings as a JSON array of leads, where each lead "
            "includes comprehensive context and details. Format: "
            '[{"context": "Lead description with comprehensive details..."}]'
        )

    @pytest.fixture
    def mock_clients(self):
        """Mock all clients for integration testing."""
        mock_openai = Mock()
        mock_perplexity = Mock()
        mock_pinecone = Mock()
        mock_mongodb = Mock()

        # Set up discovery response
        discovery_json = json.dumps(
            [
                {
                    "context": "Climate Summit 2024: Global climate leaders meet to "
                    "establish comprehensive environmental policies."
                },
                {
                    "context": "AI Breakthrough Announced: Major AI advancement in "
                    "healthcare diagnostics revolutionizes medical practice."
                },
            ]
        )
        mock_perplexity.deep_research.return_value = discovery_json

        # Set up deduplication (no duplicates)
        mock_openai.embed_text.return_value = [0.1] * 1536
        mock_pinecone.similarity_search.return_value = []

        # Set up decision response
        mock_openai.chat_completion.return_value = "1, 2"

        # Set up research response
        research_responses = [
            json.dumps(
                {
                    "headline": "Global Climate Summit Sets Ambitious 2030 Targets",
                    "summary": "World leaders at the 2024 Climate Summit agreed on "
                    "unprecedented carbon reduction goals.",
                    "body": "In a historic gathering, the 2024 Climate Summit "
                    "concluded with ambitious commitments.",
                    "sources": [
                        "https://example.com/climate-summit",
                        "https://example.com/carbon-targets",
                    ],
                }
            ),
            json.dumps(
                {
                    "headline": "AI Revolution in Healthcare Diagnostics",
                    "summary": "Breakthrough AI system shows promise in medical "
                    "diagnosis and drug discovery.",
                    "body": "Researchers have developed an AI system that "
                    "revolutionizes healthcare diagnostics.",
                    "sources": [
                        "https://example.com/ai-health",
                        "https://example.com/medical-ai",
                    ],
                }
            ),
        ]
        mock_perplexity.research.side_effect = research_responses

        # Set up storage
        mock_mongodb.insert_story.return_value = "64a7b8c9d1e2f3a4b5c6d7e8"

        return {
            "openai": mock_openai,
            "perplexity": mock_perplexity,
            "pinecone": mock_pinecone,
            "mongodb": mock_mongodb,
        }

    @pytest.mark.integration
    def test_complete_pipeline_success(self, mock_clients, test_discovery_instructions):
        """Test complete pipeline from discovery to storage."""

        with patch(
            "services.lead_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute complete pipeline
            leads = discover_leads(mock_clients["perplexity"])
            unique_leads = deduplicate_leads(
                leads,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_leads = curate_leads(
                unique_leads, openai_client=mock_clients["openai"]
            )
            stories = research_story(
                prioritized_leads, perplexity_client=mock_clients["perplexity"]
            )
            persist_stories(stories, mongodb_client=mock_clients["mongodb"])

        # Verify pipeline flow
        assert len(leads) == 2
        assert len(unique_leads) == 2  # No duplicates removed
        assert len(prioritized_leads) == 2  # Decision selected both leads
        assert len(stories) == 2

        # Verify data flow through pipeline
        # Leads from discovery
        assert "Climate Summit 2024" in leads[0].context
        assert "AI Breakthrough Announced" in leads[1].context

        # Stories from research
        assert (
            stories[0].headline == "Global Climate Summit Sets Ambitious 2030 Targets"
        )
        assert stories[1].headline == "AI Revolution in Healthcare Diagnostics"

        # Verify clients were called appropriately
        mock_clients["perplexity"].deep_research.assert_called_once()
        assert mock_clients["openai"].embed_text.call_count == 2  # One per lead
        assert mock_clients["perplexity"].research.call_count == 2  # One per story
        assert mock_clients["mongodb"].insert_story.call_count == 2

    @pytest.mark.integration
    def test_pipeline_with_deduplication(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline behavior when deduplication removes leads."""
        # Modify similarity search to simulate duplicates - provide enough responses
        mock_clients["pinecone"].similarity_search.side_effect = [
            [("existing-1", 0.95)],  # First lead is duplicate
            [],  # Second lead is unique
            [],  # Third lead is unique
            [],  # Fourth lead is unique
            [],  # Fifth lead is unique
        ]

        # Set up discovery with duplicate leads
        discovery_json = json.dumps(
            [
                {"context": "Lead 1: First lead description"},
                {"context": "Lead 2: Second lead description"},
                {"context": "Lead 3: Similar to Lead 1"},
                {"context": "Lead 4: Fourth lead description"},
                {"context": "Lead 5: Fifth lead description"},
            ]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_json

        # Set up hybrid curator responses - evaluation and pairwise comparison
        evaluation_response = json.dumps(
            [
                {
                    "index": 1,
                    "impact": 8,
                    "proximity": 7,
                    "prominence": 7,
                    "relevance": 8,
                    "hook": 6,
                    "novelty": 5,
                    "conflict": 4,
                    "brief_reasoning": "High impact lead",
                },
                {
                    "index": 2,
                    "impact": 9,
                    "proximity": 8,
                    "prominence": 8,
                    "relevance": 9,
                    "hook": 7,
                    "novelty": 6,
                    "conflict": 5,
                    "brief_reasoning": "Very high impact lead",
                },
                {
                    "index": 3,
                    "impact": 5,
                    "proximity": 6,
                    "prominence": 5,
                    "relevance": 5,
                    "hook": 4,
                    "novelty": 3,
                    "conflict": 2,
                    "brief_reasoning": "Lower impact lead",
                },  # This should be filtered out
                {
                    "index": 4,
                    "impact": 8,
                    "proximity": 7,
                    "prominence": 7,
                    "relevance": 8,
                    "hook": 6,
                    "novelty": 5,
                    "conflict": 4,
                    "brief_reasoning": "High impact lead",
                },
            ]
        )
        pairwise_response = json.dumps(
            [{"pair": "1vs2", "winner": 2, "confidence": "high"}]
        )
        mock_clients["openai"].chat_completion.side_effect = [
            evaluation_response,
            pairwise_response,
        ]

        with patch(
            "services.lead_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline
            leads = discover_leads(mock_clients["perplexity"])
            unique_leads = deduplicate_leads(
                leads,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_leads = curate_leads(
                unique_leads, openai_client=mock_clients["openai"]
            )

        # Verify deduplication worked
        assert len(leads) == 5  # Original count
        assert len(unique_leads) == 4  # One duplicate removed
        assert len(prioritized_leads) == 3  # Decision selected 3/4 leads

        # Verify selected leads are the expected ones
        # (order may vary due to hybrid scoring)
        selected_contexts = [lead.context for lead in prioritized_leads]
        # Lead 2 selected
        assert any("Lead 2" in context for context in selected_contexts)
        # Lead 3 selected
        assert any("Lead 3" in context for context in selected_contexts)
        # Lead 5 selected
        assert any("Lead 5" in context for context in selected_contexts)
        # Lead 4 filtered
        assert not any("Lead 4" in context for context in selected_contexts)

    def test_pipeline_data_transformation(
        self, mock_clients, test_discovery_instructions
    ):
        """Test data transformation through pipeline stages."""

        # Mock simple discovery response
        discovery_json = json.dumps([{"context": "Original Lead: Original summary"}])
        mock_clients["perplexity"].deep_research.return_value = discovery_json

        # Override the global mock with specific response for this test
        research_json = json.dumps(
            {
                "headline": "Transformed Headline",
                "summary": "Enhanced summary",
                "body": "Detailed story body",
                "sources": ["https://source1.com", "https://source2.com"],
            }
        )
        mock_clients["perplexity"].research.return_value = research_json
        mock_clients["perplexity"].research.side_effect = None  # Reset side_effect

        # Set up decision response for single lead
        mock_clients["openai"].chat_completion.return_value = "1"

        with patch(
            "services.lead_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline and track transformations
            leads = discover_leads(mock_clients["perplexity"])
            unique_leads = deduplicate_leads(
                leads,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_leads = curate_leads(
                unique_leads, openai_client=mock_clients["openai"]
            )
            stories = research_story(
                prioritized_leads, perplexity_client=mock_clients["perplexity"]
            )

            # Store final stories
            persist_stories(stories, mongodb_client=mock_clients["mongodb"])

        # Verify data transformations
        # Lead -> Lead (deduplication preserves structure)
        assert isinstance(leads[0], Lead)
        assert isinstance(unique_leads[0], Lead)
        assert leads[0].context == unique_leads[0].context

        # Lead -> Lead (decision preserves structure, filters by impact)
        assert isinstance(prioritized_leads[0], Lead)
        assert prioritized_leads[0].context == unique_leads[0].context

        # Lead -> Story (research transforms and enhances)
        assert isinstance(stories[0], Story)
        assert stories[0].headline == "Transformed Headline"
        assert (
            stories[0].summary != prioritized_leads[0].context
        )  # Enhanced by research
        assert len(stories[0].sources) == 2

    def test_large_scale_pipeline(self, mock_clients, test_discovery_instructions):
        """Test pipeline performance with larger data volume."""

        # Create large discovery response
        discovery_data = [{"context": f"Lead {i}: Summary {i}"} for i in range(1, 11)]
        discovery_json = json.dumps(discovery_data)
        mock_clients["perplexity"].deep_research.return_value = discovery_json

        # Set up decision to select subset
        mock_clients["openai"].chat_completion.return_value = "1, 3, 5, 7, 9"

        # Override research responses for 5 stories
        research_responses = [
            json.dumps(
                {
                    "headline": f"Story {i}",
                    "summary": f"Summary {i}",
                    "body": f"Body {i}",
                    "sources": [f"https://source{i}.com"],
                }
            )
            for i in [1, 3, 5, 7, 9]
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        with patch(
            "services.lead_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline
            leads = discover_leads(mock_clients["perplexity"])
            unique_leads = deduplicate_leads(
                leads,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_leads = curate_leads(
                unique_leads, openai_client=mock_clients["openai"]
            )
            stories = research_story(
                prioritized_leads, perplexity_client=mock_clients["perplexity"]
            )

        # Verify scalability
        assert len(leads) == 10
        assert len(unique_leads) == 10  # No duplicates
        assert len(prioritized_leads) == 5  # Decision selected 5
        assert len(stories) == 5

        # Verify embeddings were created for all leads
        assert mock_clients["openai"].embed_text.call_count == 10

        # Verify research was called for all selected leads
        assert mock_clients["perplexity"].research.call_count == 5
