"""Integration tests for services pipeline."""

import json
from unittest.mock import Mock, patch

import pytest

from services import (
    deduplicate_leads,
    discover_leads,
    insert_articles,
    research_articles,
    curate_leads,
)
from models import Lead, Story


@pytest.mark.integration
class TestServicesIntegration:
    """Integration tests showing how services work together."""

    @pytest.fixture
    def test_discovery_instructions(self):
        """Test-specific discovery instructions with fixed date."""
        return (
            "Identify significant news about climate, environment and natural "
            "disasters, and major geopolitical events from today 2024-01-15. "
            "Focus on major global developments, breaking news, and important "
            "updates that would be of interest to a general audience. "
            "Return your findings as a JSON array of events, where each event "
            "has a 'context' field. Example format: "
            '[{"context": "Event description with comprehensive details..."}]'
        )

    @pytest.fixture
    def mock_clients(self):
        """Mock all clients for integration testing."""
        mock_openai = Mock()
        mock_perplexity = Mock()
        mock_pinecone = Mock()
        mock_mongodb = Mock()

        # Set up discovery response
        discovery_json = json.dumps([
            {"context": "Climate Summit 2024: Global climate leaders meet to establish comprehensive environmental policies."},
            {"context": "AI Breakthrough Announced: Major AI advancement in healthcare diagnostics revolutionizes medical practice."},
        ])
        mock_perplexity.deep_research.return_value = discovery_json

        # Set up deduplication (no duplicates)
        mock_openai.embed_text.return_value = [0.1] * 1536
        mock_pinecone.similarity_search.return_value = []

        # Set up decision response
        mock_openai.chat_completion.return_value = "1, 2"

        # Set up research response
        research_responses = [
            json.dumps({
                "headline": "Global Climate Summit Sets Ambitious 2030 Targets",
                "summary": "World leaders at the 2024 Climate Summit agreed on unprecedented carbon reduction goals.",
                "body": "In a historic gathering, the 2024 Climate Summit concluded with ambitious commitments.",
                "sources": ["https://example.com/climate-summit", "https://example.com/carbon-targets"]
            }),
            json.dumps({
                "headline": "AI Revolution in Healthcare Diagnostics",
                "summary": "Breakthrough AI system shows promise in medical diagnosis and drug discovery.",
                "body": "Researchers have developed an AI system that revolutionizes healthcare diagnostics.",
                "sources": ["https://example.com/ai-health", "https://example.com/medical-ai"]
            })
        ]
        mock_perplexity.research.side_effect = research_responses

        # Set up storage
        mock_mongodb.insert_article.return_value = "64a7b8c9d1e2f3a4b5c6d7e8"

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
            events = discover_leads(mock_clients["perplexity"])
            unique_events = deduplicate_leads(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = curate_leads(
                unique_events, openai_client=mock_clients["openai"]
            )
            articles = research_articles(
                prioritized_events, perplexity_client=mock_clients["perplexity"]
            )
            insert_articles(articles, mongodb_client=mock_clients["mongodb"])

        # Verify pipeline flow
        assert len(events) == 2
        assert len(unique_events) == 2  # No duplicates removed
        assert len(prioritized_events) == 2  # Decision selected both events
        assert len(articles) == 2

        # Verify data flow through pipeline
        # Events from discovery
        assert "Climate Summit 2024" in events[0].context
        assert "AI Breakthrough Announced" in events[1].context

        # Articles from research
        assert (
            articles[0].headline == "Global Climate Summit Sets Ambitious 2030 Targets"
        )
        assert articles[1].headline == "AI Revolution in Healthcare Diagnostics"

        # Verify clients were called appropriately
        mock_clients["perplexity"].deep_research.assert_called_once()
        assert mock_clients["openai"].embed_text.call_count == 2  # One per event
        assert mock_clients["perplexity"].research.call_count == 2  # One per article
        assert mock_clients["mongodb"].insert_article.call_count == 2

    @pytest.mark.integration  
    def test_pipeline_with_deduplication(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline behavior when deduplication removes events."""
        # Modify similarity search to simulate duplicates - provide enough responses
        mock_clients["pinecone"].similarity_search.side_effect = [
            [("existing-1", 0.95)],  # First event is duplicate
            [],  # Second event is unique
            [],  # Third event is unique
            [],  # Fourth event is unique
            [],  # Fifth event is unique
        ]

        # Set up discovery with duplicate events
        discovery_json = json.dumps([
            {"context": "Event 1: First event description"},
            {"context": "Event 2: Second event description"},
            {"context": "Event 3: Similar to Event 1"},
            {"context": "Event 4: Fourth event description"},
            {"context": "Event 5: Fifth event description"},
        ])
        mock_clients["perplexity"].deep_research.return_value = discovery_json

        # Set up decision response - events 1, 2, 4 from the remaining 4 unique events
        mock_clients["openai"].chat_completion.return_value = "1, 2, 4"

        with patch(
            "services.lead_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline
            events = discover_leads(mock_clients["perplexity"])
            unique_events = deduplicate_leads(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = curate_leads(
                unique_events, openai_client=mock_clients["openai"]
            )

        # Verify deduplication worked
        assert len(events) == 5  # Original count
        assert len(unique_events) == 4  # One duplicate removed
        assert len(prioritized_events) == 3  # Decision selected 3/4 events

        # Verify selected articles correspond to selected events
        assert "Event 2" in prioritized_events[0].context  # Index 1 -> Event 2 (since Event 1 was duplicate)
        assert "Event 3" in prioritized_events[1].context  # Index 2 -> Event 3  
        assert "Event 5" in prioritized_events[2].context  # Index 4 -> Event 5

    def test_pipeline_data_transformation(
        self, mock_clients, test_discovery_instructions
    ):
        """Test data transformation through pipeline stages."""
        
        # Mock simple discovery response
        discovery_json = json.dumps([
            {"context": "Original Event: Original summary"}
        ])
        mock_clients["perplexity"].deep_research.return_value = discovery_json

        # Override the global mock with specific response for this test
        research_json = json.dumps({
            "headline": "Transformed Headline",
            "summary": "Enhanced summary",
            "body": "Detailed article body",
            "sources": ["https://source1.com", "https://source2.com"]
        })
        mock_clients["perplexity"].research.return_value = research_json
        mock_clients["perplexity"].research.side_effect = None  # Reset side_effect

        # Set up decision response for single event
        mock_clients["openai"].chat_completion.return_value = "1"

        with patch(
            "services.lead_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline and track transformations
            events = discover_leads(mock_clients["perplexity"])
            unique_events = deduplicate_leads(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = curate_leads(
                unique_events, openai_client=mock_clients["openai"]
            )
            articles = research_articles(
                prioritized_events, perplexity_client=mock_clients["perplexity"]
            )

            # Store final articles
            insert_articles(articles, mongodb_client=mock_clients["mongodb"])

        # Verify data transformations
        # Lead -> Lead (deduplication preserves structure)
        assert isinstance(events[0], Lead)
        assert isinstance(unique_events[0], Lead)
        assert events[0].context == unique_events[0].context

        # Lead -> Lead (decision preserves structure, filters by impact)
        assert isinstance(prioritized_events[0], Lead)
        assert prioritized_events[0].context == unique_events[0].context

        # Lead -> Story (research transforms and enhances)
        assert isinstance(articles[0], Story)
        assert articles[0].headline == "Transformed Headline"
        assert (
            articles[0].summary != prioritized_events[0].context
        )  # Enhanced by research
        assert len(articles[0].sources) == 2

    def test_large_scale_pipeline(self, mock_clients, test_discovery_instructions):
        """Test pipeline performance with larger data volume."""
        
        # Create large discovery response
        discovery_data = [{"context": f"Event {i}: Summary {i}"} for i in range(1, 11)]
        discovery_json = json.dumps(discovery_data)
        mock_clients["perplexity"].deep_research.return_value = discovery_json

        # Set up decision to select subset
        mock_clients["openai"].chat_completion.return_value = "1, 3, 5, 7, 9"

        # Override research responses for 5 articles
        research_responses = [
            json.dumps({
                "headline": f"Article {i}",
                "summary": f"Summary {i}",
                "body": f"Body {i}",
                "sources": [f"https://source{i}.com"]
            }) for i in [1, 3, 5, 7, 9]
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        with patch(
            "services.lead_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline
            events = discover_leads(mock_clients["perplexity"])
            unique_events = deduplicate_leads(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = curate_leads(
                unique_events, openai_client=mock_clients["openai"]
            )
            articles = research_articles(
                prioritized_events, perplexity_client=mock_clients["perplexity"]
            )

        # Verify scalability
        assert len(events) == 10
        assert len(unique_events) == 10  # No duplicates
        assert len(prioritized_events) == 5  # Decision selected 5
        assert len(articles) == 5

        # Verify embeddings were created for all events
        assert mock_clients["openai"].embed_text.call_count == 10
        
        # Verify research was called for all selected events
        assert mock_clients["perplexity"].research.call_count == 5
