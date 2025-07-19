"""Integration tests for services pipeline."""

import json
from unittest.mock import Mock

import pytest

from models import Lead, Story
from services import (
    curate_leads,
    deduplicate_leads,
    discover_leads,
    persist_stories,
    research_lead,
    write_stories,
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
            '[{"title": "Lead description with comprehensive details..."}]'
        )

    @pytest.fixture
    def mock_clients(self):
        """Mock all clients for integration testing."""
        mock_openai = Mock()
        mock_perplexity = Mock()
        mock_pinecone = Mock()
        mock_mongodb = Mock()

        # Set up discovery responses for three categories
        politics_response = json.dumps([{"title": "Political Summit 2024: World leaders discuss global governance and international cooperation."}])
        environment_response = json.dumps(
            [{"title": "Climate Summit 2024: Global climate leaders meet to establish comprehensive environmental policies."}]
        )
        entertainment_response = json.dumps(
            [{"title": "AI Breakthrough Announced: Major AI advancement in healthcare diagnostics revolutionizes medical practice."}]
        )

        # Set lead_discovery to return different responses for each call
        mock_perplexity.lead_discovery.side_effect = [
            politics_response,
            environment_response,
            entertainment_response,
        ]

        # Set up deduplication (no duplicates)
        mock_openai.embed_text.return_value = [0.1] * 1536
        mock_pinecone.similarity_search.return_value = []

        # Set up curation response (will be overridden by side_effect)
        mock_openai.chat_completion.return_value = "1, 2, 3"

        # Set up lead research responses (context + sources)
        lead_research_responses = [
            json.dumps(
                {
                    "context": (
                        "Political leaders from around the world gathered to discuss international cooperation and global governance frameworks."
                    ),
                    "sources": [
                        "https://example.com/political-summit",
                        "https://example.com/governance",
                    ],
                }
            ),
            json.dumps(
                {
                    "context": (
                        "The 2024 Climate Summit brought together world leaders to "
                        "establish comprehensive environmental policies and carbon "
                        "reduction goals."
                    ),
                    "sources": [
                        "https://example.com/climate-summit",
                        "https://example.com/carbon-targets",
                    ],
                }
            ),
            json.dumps(
                {
                    "context": (
                        "Researchers have developed breakthrough AI technology that revolutionizes healthcare diagnostics and medical practice."
                    ),
                    "sources": [
                        "https://example.com/ai-health",
                        "https://example.com/medical-ai",
                    ],
                }
            ),
        ]
        mock_perplexity.lead_research.side_effect = lead_research_responses

        # Set up query formulation responses (for research service)
        query_formulation_responses = [
            "political summit world leaders international cooperation",
            "climate summit 2024 environmental policies carbon targets",
            "AI breakthrough healthcare diagnostics medical technology",
        ]

        # Set up story writing responses (headline + summary + body)
        story_writing_responses = [
            json.dumps(
                {
                    "headline": "World Leaders Unite at Political Summit",
                    "summary": ("Political leaders agree on new international cooperation framework."),
                    "body": ("In a historic gathering, world leaders came together to discuss global governance."),
                }
            ),
            json.dumps(
                {
                    "headline": "Global Climate Summit Sets Ambitious 2030 Targets",
                    "summary": ("World leaders at the 2024 Climate Summit agreed on unprecedented carbon reduction goals."),
                    "body": ("In a historic gathering, the 2024 Climate Summit concluded with ambitious commitments."),
                }
            ),
            json.dumps(
                {
                    "headline": "AI Revolution in Healthcare Diagnostics",
                    "summary": ("Breakthrough AI system shows promise in medical diagnosis and drug discovery."),
                    "body": ("Researchers have developed an AI system that revolutionizes healthcare diagnostics."),
                }
            ),
        ]
        # Set up curation response
        curation_response = json.dumps(
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
                        "brief_reasoning": "High quality political lead",
                    },
                    {
                        "index": 2,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality environmental lead",
                    },
                    {
                        "index": 3,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality AI lead",
                    },
                ]
            }
        )

        # Set up chat_completion to handle all calls: 1 curation + 3 query formulation + 3 story writing = 7 calls
        mock_openai.chat_completion.side_effect = (
            [curation_response]  # 1 curation call
            + query_formulation_responses  # 3 query formulation calls
            + story_writing_responses  # 3 story writing calls
        )

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

        # No need to patch DISCOVERY_INSTRUCTIONS anymore since we're using
        # category-specific ones
        # Execute complete pipeline
        leads = discover_leads(mock_clients["perplexity"])
        unique_leads = deduplicate_leads(
            leads,
            openai_client=mock_clients["openai"],
            pinecone_client=mock_clients["pinecone"],
        )
        prioritized_leads = curate_leads(unique_leads, openai_client=mock_clients["openai"])
        researched_leads = research_lead(prioritized_leads, openai_client=mock_clients["openai"], perplexity_client=mock_clients["perplexity"])
        stories = write_stories(researched_leads, openai_client=mock_clients["openai"])
        persist_stories(stories, mongodb_client=mock_clients["mongodb"])

        # Verify pipeline flow
        assert len(leads) == 3  # One from each category
        assert len(unique_leads) == 3  # No duplicates removed
        assert len(prioritized_leads) == 3  # Decision selected all leads
        assert len(researched_leads) == 3  # All leads researched
        assert len(stories) == 3  # All leads converted to stories

        # Verify data flow through pipeline
        # Leads from discovery
        assert "Political Summit 2024" in leads[0].title
        assert "Climate Summit 2024" in leads[1].title
        assert "AI Breakthrough Announced" in leads[2].title

        # Researched leads have context
        assert "international cooperation" in researched_leads[0].context
        assert "environmental policies" in researched_leads[1].context
        assert "breakthrough AI technology" in researched_leads[2].context

        # Stories from writing
        assert stories[0].headline == "World Leaders Unite at Political Summit"
        assert stories[1].headline == ("Global Climate Summit Sets Ambitious 2030 Targets")
        assert stories[2].headline == "AI Revolution in Healthcare Diagnostics"

        # Verify clients were called appropriately
        assert mock_clients["perplexity"].lead_discovery.call_count == 3  # Three category calls
        # One per lead for deduplication
        assert mock_clients["openai"].embed_text.call_count == 3
        # One per lead for research
        assert mock_clients["perplexity"].lead_research.call_count == 3
        # 1 for curation + 3 for query formulation + 3 for story writing = 7 calls
        assert mock_clients["openai"].chat_completion.call_count == 7
        assert mock_clients["mongodb"].insert_story.call_count == 3

    @pytest.mark.integration
    def test_pipeline_with_deduplication(self, mock_clients, test_discovery_instructions):
        """Test pipeline behavior when deduplication removes leads."""
        # Modify similarity search to simulate duplicates - provide enough responses
        mock_clients["pinecone"].similarity_search.side_effect = [
            [("existing-1", 0.95)],  # First lead is duplicate
            [],  # Second lead is unique
            [],  # Third lead is unique
            [],  # Fourth lead is unique
            [],  # Fifth lead is unique
        ]

        # Set up discovery with multiple leads per category
        politics_json = json.dumps(
            [
                            {"title": "Lead 1: First political lead description"},
            {"title": "Lead 2: Second political lead description"},
            ]
        )
        environment_json = json.dumps(
            [
                {"title": "Lead 3: Environmental lead description"},
            ]
        )
        entertainment_json = json.dumps(
            [
                            {"title": "Lead 4: Entertainment lead description"},
            {"title": "Lead 5: Sports lead description"},
            ]
        )
        mock_clients["perplexity"].lead_discovery.side_effect = [
            politics_json,
            environment_json,
            entertainment_json,
        ]

        # Set up curator responses - evaluation and pairwise comparison
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
        pairwise_response = json.dumps([{"pair": "1vs2", "winner": 2, "confidence": "high"}])
        mock_clients["openai"].chat_completion.side_effect = [
            evaluation_response,
            pairwise_response,
        ]

        # Execute pipeline
        leads = discover_leads(mock_clients["perplexity"])
        unique_leads = deduplicate_leads(
            leads,
            openai_client=mock_clients["openai"],
            pinecone_client=mock_clients["pinecone"],
        )
        prioritized_leads = curate_leads(unique_leads, openai_client=mock_clients["openai"])

        # Verify deduplication worked
        assert len(leads) == 5  # Original count across all categories
        assert len(unique_leads) == 4  # One duplicate removed
        assert len(prioritized_leads) == 3  # Decision selected 3/4 leads

        # Verify selected leads are the expected ones
        # (order may vary due to scoring)
        selected_titles = [lead.title for lead in prioritized_leads]
        # Lead 2 selected
        assert any("Lead 2" in title for title in selected_titles)
        # Lead 3 selected
        assert any("Lead 3" in title for title in selected_titles)
        # Lead 5 selected
        assert any("Lead 5" in title for title in selected_titles)
        # Lead 4 filtered
        assert not any("Lead 4" in title for title in selected_titles)

    def test_pipeline_data_transformation(self, mock_clients, test_discovery_instructions):
        """Test data transformation through pipeline stages."""

        # Mock simple discovery response - one lead per category
        politics_json = json.dumps([{"title": "Political Lead: Political news"}])
        environment_json = json.dumps([{"title": "Environmental Lead: Climate news"}])
        entertainment_json = json.dumps([{"title": "Entertainment Lead: Celebrity news"}])

        mock_clients["perplexity"].lead_discovery.side_effect = [
            politics_json,
            environment_json,
            entertainment_json,
        ]

        # Override the global mock with specific response for this test
        lead_research_json = json.dumps(
            {
                "context": "Enhanced context with research details",
                "sources": ["https://source1.com", "https://source2.com"],
            }
        )
        mock_clients["perplexity"].lead_research.return_value = lead_research_json
        # Reset side_effect
        mock_clients["perplexity"].lead_research.side_effect = None

        # Set up story writing response
        story_writing_json = json.dumps(
            {
                "headline": "Transformed Headline",
                "summary": "Enhanced summary",
                "body": "Detailed story body",
            }
        )

        # Set up all OpenAI responses: 1 curation + 3 query formulation + 3 story writing = 7 total
        curation_response = json.dumps(
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
                        "brief_reasoning": "High quality lead",
                    },
                    {
                        "index": 2,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality lead",
                    },
                    {
                        "index": 3,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality lead",
                    },
                ]
            }
        )

        mock_clients["openai"].chat_completion.side_effect = [
            curation_response,  # 1 curation call
            "transformed search query 1",  # Query formulation for lead 1
            "transformed search query 2",  # Query formulation for lead 2
            "transformed search query 3",  # Query formulation for lead 3
            story_writing_json,  # Story writing for lead 1
            story_writing_json,  # Story writing for lead 2
            story_writing_json,  # Story writing for lead 3
        ]

        # Execute pipeline and track transformations
        leads = discover_leads(mock_clients["perplexity"])
        unique_leads = deduplicate_leads(
            leads,
            openai_client=mock_clients["openai"],
            pinecone_client=mock_clients["pinecone"],
        )
        prioritized_leads = curate_leads(unique_leads, openai_client=mock_clients["openai"])
        researched_leads = research_lead(prioritized_leads, openai_client=mock_clients["openai"], perplexity_client=mock_clients["perplexity"])
        stories = write_stories(researched_leads, openai_client=mock_clients["openai"])

        # Store final stories
        persist_stories(stories, mongodb_client=mock_clients["mongodb"])

        # Verify data transformations
        # Lead -> Lead (deduplication preserves structure)
        assert isinstance(leads[0], Lead)
        assert isinstance(unique_leads[0], Lead)
        assert leads[0].title == unique_leads[0].title

        # Lead -> Lead (curation preserves structure, filters by impact)
        assert isinstance(prioritized_leads[0], Lead)
        assert prioritized_leads[0].title in [lead.title for lead in unique_leads]

        # Lead -> Enhanced Lead (research adds context and sources)
        assert len(researched_leads) == 3
        assert isinstance(researched_leads[0], Lead)
        assert researched_leads[0].context == ("Enhanced context with research details")
        assert len(researched_leads[0].sources) == 2

        # Enhanced Lead -> Story (writing transforms to full story)
        assert len(stories) == 3
        assert isinstance(stories[0], Story)
        assert stories[0].headline == "Transformed Headline"
        assert stories[0].summary == "Enhanced summary"
        # Sources preserved from research
        assert stories[0].sources == researched_leads[0].sources

    def test_large_scale_pipeline(self, mock_clients, test_discovery_instructions):
        """Test pipeline performance with larger data volume."""

        # Create large discovery responses across categories
        politics_data = [{"title": f"Political Lead {i}: Political news {i}"} for i in range(1, 5)]
        environment_data = [{"title": f"Environmental Lead {i}: Climate news {i}"} for i in range(5, 8)]
        entertainment_data = [{"title": f"Entertainment Lead {i}: Celebrity news {i}"} for i in range(8, 11)]

        mock_clients["perplexity"].lead_discovery.side_effect = [
            json.dumps(politics_data),
            json.dumps(environment_data),
            json.dumps(entertainment_data),
        ]

        # Set up curation response to evaluate all 10 leads and select 5
        large_scale_curation_response = json.dumps(
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
                        "brief_reasoning": "High quality lead",
                    },
                    {
                        "index": 2,
                        "impact": 5,  # Lower score to exclude
                        "proximity": 5,
                        "prominence": 5,
                        "relevance": 5,
                        "hook": 5,
                        "novelty": 5,
                        "conflict": 5,
                        "brief_reasoning": "Lower quality lead",
                    },
                    {
                        "index": 3,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality lead",
                    },
                    {
                        "index": 4,
                        "impact": 5,  # Lower score to exclude
                        "proximity": 5,
                        "prominence": 5,
                        "relevance": 5,
                        "hook": 5,
                        "novelty": 5,
                        "conflict": 5,
                        "brief_reasoning": "Lower quality lead",
                    },
                    {
                        "index": 5,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality lead",
                    },
                    {
                        "index": 6,
                        "impact": 5,  # Lower score to exclude
                        "proximity": 5,
                        "prominence": 5,
                        "relevance": 5,
                        "hook": 5,
                        "novelty": 5,
                        "conflict": 5,
                        "brief_reasoning": "Lower quality lead",
                    },
                    {
                        "index": 7,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality lead",
                    },
                    {
                        "index": 8,
                        "impact": 5,  # Lower score to exclude
                        "proximity": 5,
                        "prominence": 5,
                        "relevance": 5,
                        "hook": 5,
                        "novelty": 5,
                        "conflict": 5,
                        "brief_reasoning": "Lower quality lead",
                    },
                    {
                        "index": 9,
                        "impact": 8,
                        "proximity": 8,
                        "prominence": 8,
                        "relevance": 8,
                        "hook": 8,
                        "novelty": 8,
                        "conflict": 8,
                        "brief_reasoning": "High quality lead",
                    },
                    {
                        "index": 10,
                        "impact": 5,  # Lower score to exclude
                        "proximity": 5,
                        "prominence": 5,
                        "relevance": 5,
                        "hook": 5,
                        "novelty": 5,
                        "conflict": 5,
                        "brief_reasoning": "Lower quality lead",
                    },
                ]
            }
        )

        # Set up all responses for this test: 1 curation + 5 query formulation
        query_formulation_responses = [f"optimized query {i}" for i in [1, 3, 5, 7, 9]]

        mock_clients["openai"].chat_completion.side_effect = (
            [large_scale_curation_response]  # 1 curation call
            + query_formulation_responses  # 5 query formulation calls
        )

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
        mock_clients["perplexity"].lead_research.side_effect = research_responses

        # Execute pipeline
        leads = discover_leads(mock_clients["perplexity"])
        unique_leads = deduplicate_leads(
            leads,
            openai_client=mock_clients["openai"],
            pinecone_client=mock_clients["pinecone"],
        )
        prioritized_leads = curate_leads(unique_leads, openai_client=mock_clients["openai"])
        stories = research_lead(prioritized_leads, openai_client=mock_clients["openai"], perplexity_client=mock_clients["perplexity"])

        # Verify scalability
        assert len(leads) == 10  # 4 + 3 + 3 from three categories
        assert len(unique_leads) == 10  # No duplicates
        assert len(prioritized_leads) == 5  # Decision selected 5
        assert len(stories) == 5

        # Verify embeddings were created for all leads
        assert mock_clients["openai"].embed_text.call_count == 10

        # Verify research was called for all selected leads
        assert mock_clients["perplexity"].lead_research.call_count == 5
