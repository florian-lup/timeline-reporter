"""Integration tests for services pipeline."""

import json
from unittest.mock import Mock, patch

import pytest

from services import (
    deduplicate_events,
    discover_events,
    insert_articles,
    research_articles,
    select_events,
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
            "has 'title' and 'summary' fields. Example format: "
            '[{"title": "Event Title", "summary": "Brief description..."}]'
        )

    @pytest.fixture
    def mock_clients(self):
        """Mock all clients for integration testing."""
        mock_openai = Mock()
        mock_perplexity = Mock()
        mock_pinecone = Mock()
        mock_mongodb = Mock()

        return {
            "openai": mock_openai,
            "perplexity": mock_perplexity,
            "pinecone": mock_pinecone,
            "mongodb": mock_mongodb,
        }

    def test_complete_pipeline_success(self, mock_clients, test_discovery_instructions):
        """Test complete 5-step pipeline success."""
        # 1. Discovery Service Mocks
        discovery_response = json.dumps(
            [
                {"title": "Climate Summit 2024", "summary": "Global climate leaders..."},
                {"title": "AI Breakthrough Announced", "summary": "Major AI advancement..."},
            ]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # 2. Deduplication Service Mocks
        mock_clients["openai"].embed_text.side_effect = [
            [0.1] * 1536,  # Event 1 embedding
            [0.9] * 1536,  # Event 2 embedding (different)
        ]
        mock_clients["pinecone"].similarity_search.side_effect = [
            [],  # No similar events for event 1
            [],  # No similar events for event 2
        ]

        # 3. Decision Service Mocks
        mock_clients["openai"].chat_completion.return_value = "1, 2"  # Select both events

        # 4. Research Service Mocks
        research_responses = [
            json.dumps({
                "headline": "Global Climate Summit Sets Ambitious 2030 Targets",
                "summary": "World leaders at the climate summit agree...",
                "body": "In a historic moment, global leaders...",
                "sources": ["https://climate-summit.com", "https://example.com"],
            }),
            json.dumps({
                "headline": "AI Revolution in Healthcare Diagnostics",
                "summary": "Breakthrough AI system shows promise...",
                "body": "Researchers have developed an AI system...",
                "sources": ["https://ai-health.com", "https://example.com"],
            }),
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # 5. Storage Service Mocks
        mock_clients["mongodb"].insert_article.side_effect = [
            "60a1b2c3d4e5f6789",
            "60a1b2c3d4e5f6790",
        ]

        # Execute complete pipeline
        with patch(
            "services.event_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # 1. Discovery
            events = discover_events(mock_clients["perplexity"])

            # 2. Deduplication
            unique_events = deduplicate_events(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )

            # 3. Decision (prioritize most impactful events)
            prioritized_events = select_events(
                unique_events, openai_client=mock_clients["openai"]
            )

            # 4. Research
            articles = research_articles(
                prioritized_events, perplexity_client=mock_clients["perplexity"]
            )

            # 5. Storage
            insert_articles(articles, mongodb_client=mock_clients["mongodb"])

        # Verify pipeline results
        assert len(events) == 2
        assert len(unique_events) == 2  # No duplicates filtered
        assert len(prioritized_events) == 2  # Both events selected by decision service
        assert len(articles) == 2

        # Verify data flow through pipeline
        # Events from discovery
        assert events[0].title == "Climate Summit 2024"
        assert events[1].title == "AI Breakthrough Announced"

        # Articles from research
        assert (
            articles[0].headline == "Global Climate Summit Sets Ambitious 2030 Targets"
        )
        assert articles[1].headline == "AI Revolution in Healthcare Diagnostics"

        # Verify all clients were called
        mock_clients["perplexity"].deep_research.assert_called_once()
        assert mock_clients["openai"].embed_text.call_count == 2
        assert mock_clients["pinecone"].similarity_search.call_count == 2
        assert mock_clients["openai"].chat_completion.call_count == 1  # 1 decision
        assert mock_clients["perplexity"].research.call_count == 2
        # MongoDB called twice in storage service only = 2 total
        assert mock_clients["mongodb"].insert_article.call_count == 2

    def test_pipeline_with_deduplication(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline when deduplication filters out duplicates."""
        # Discovery returns 3 events
        discovery_response = json.dumps(
            [
                {"title": "Event 1", "summary": "Summary 1"},
                {"title": "Event 2", "summary": "Summary 2"},
                {"title": "Event 3", "summary": "Similar to Event 1"},
            ]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # Deduplication filters out Event 3 (similar to Event 1)
        mock_clients["openai"].embed_text.side_effect = [
            [0.1] * 1536,  # Event 1
            [0.9] * 1536,  # Event 2
            [0.15] * 1536,  # Event 3 (similar to Event 1)
        ]
        mock_clients["pinecone"].similarity_search.side_effect = [
            [],  # No similar for Event 1
            [],  # No similar for Event 2
            [("event_1", 0.85)],  # Event 3 similar to Event 1
        ]

        # Research processes 2 remaining events
        research_responses = [
            json.dumps({
                "headline": "Article 1",
                "summary": "Summary 1",
                "body": "Story 1",
                "sources": ["https://source1.com"],
            }),
            json.dumps({
                "headline": "Article 2", 
                "summary": "Summary 2",
                "body": "Story 2", 
                "sources": ["https://source2.com"],
            }),
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # Decision selects remaining 2 events
        mock_clients["openai"].chat_completion.return_value = "1, 2"  # Select both remaining events

        # Storage processes 2 articles
        mock_clients["mongodb"].insert_article.side_effect = ["id1", "id2"]

        with patch(
            "services.event_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline
            events = discover_events(mock_clients["perplexity"])
            unique_events = deduplicate_events(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = select_events(
                unique_events, openai_client=mock_clients["openai"]
            )
            articles = research_articles(
                prioritized_events, perplexity_client=mock_clients["perplexity"]
            )

            # Store the articles
            insert_articles(articles, mongodb_client=mock_clients["mongodb"])

        # Verify deduplication worked
        assert len(events) == 3
        assert len(unique_events) == 2  # One duplicate filtered
        assert len(prioritized_events) == 2  # Decision kept both remaining events
        assert len(articles) == 2

    def test_pipeline_with_event_selection(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline when decision service filters events."""
        # Discovery returns 5 events
        discovery_response = json.dumps(
            [
                {"title": f"Event {i}", "summary": f"Summary {i}"}
                for i in range(1, 6)
            ]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # No duplicates in deduplication
        mock_clients["openai"].embed_text.side_effect = [
            [i * 0.1] * 1536 for i in range(1, 6)
        ]
        mock_clients["pinecone"].similarity_search.side_effect = [[] for _ in range(5)]

        # Decision selects only events 1, 3, 5
        mock_clients["openai"].chat_completion.return_value = "1, 3, 5"

        # Research processes 3 selected events
        research_responses = [
            json.dumps({
                "headline": f"Article {i}",
                "summary": f"Summary {i}",
                "body": f"Story {i}",
                "sources": [f"https://source{i}.com"],
            })
            for i in [1, 3, 5]
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # Storage processes 3 articles
        mock_clients["mongodb"].insert_article.side_effect = ["id1", "id3", "id5"]

        with patch(
            "services.event_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            events = discover_events(mock_clients["perplexity"])
            unique_events = deduplicate_events(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = select_events(
                unique_events, openai_client=mock_clients["openai"]
            )
            articles = research_articles(
                prioritized_events, perplexity_client=mock_clients["perplexity"]
            )

            insert_articles(articles, mongodb_client=mock_clients["mongodb"])

        # Verify decision service filtered correctly
        assert len(events) == 5
        assert len(unique_events) == 5  # No duplicates
        assert len(prioritized_events) == 3  # Decision selected 3/5 events
        assert len(articles) == 3

        # Verify selected articles correspond to selected events
        assert prioritized_events[0].title == "Event 1"
        assert prioritized_events[1].title == "Event 3"
        assert prioritized_events[2].title == "Event 5"

    def test_pipeline_data_transformation(
        self, mock_clients, test_discovery_instructions
    ):
        """Test data transformation through the pipeline."""
        # Discovery: Returns Event objects
        discovery_response = json.dumps(
            [{"title": "Original Event", "summary": "Original summary"}]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # Deduplication: Processes Event objects, returns Event objects
        mock_clients["openai"].embed_text.return_value = [0.1] * 1536
        mock_clients["pinecone"].similarity_search.return_value = []

        # Decision: Processes Event objects, returns filtered Event objects
        mock_clients["openai"].chat_completion.return_value = "1"  # Select first event

        # Research: Processes Event objects, returns Article objects
        research_response = json.dumps(
            {
                "headline": "Transformed Headline",
                "summary": "Transformed summary with more detail",
                "body": (
                    "Full story with comprehensive details about the original event"
                ),
                "sources": [
                    "https://example.com/source1",
                    "https://example.com/source2",
                ],
            }
        )
        mock_clients["perplexity"].research.return_value = research_response

        # Storage: Processes Article objects
        mock_clients["mongodb"].insert_article.return_value = "final_id"

        with patch(
            "services.event_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            # Execute pipeline and track transformations
            events = discover_events(mock_clients["perplexity"])
            unique_events = deduplicate_events(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = select_events(
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
        assert events[0].title == unique_events[0].title

        # Lead -> Lead (decision preserves structure, filters by impact)
        assert isinstance(prioritized_events[0], Lead)
        assert prioritized_events[0].title == unique_events[0].title

        # Lead -> Story (research transforms and enhances)
        assert isinstance(articles[0], Story)
        assert articles[0].headline == "Transformed Headline"
        assert (
            articles[0].summary != prioritized_events[0].summary
        )  # Enhanced by research
        assert len(articles[0].sources) == 2

    def test_empty_pipeline_flow(self, mock_clients, test_discovery_instructions):
        """Test pipeline behavior with empty results at each stage."""
        # Discovery returns no events
        mock_clients["perplexity"].deep_research.return_value = "[]"

        with patch(
            "services.event_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            events = discover_events(mock_clients["perplexity"])

            unique_events = deduplicate_events(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )

            articles = research_articles(
                unique_events, perplexity_client=mock_clients["perplexity"]
            )

        # All results should be empty
        assert events == []
        assert unique_events == []
        assert articles == []

        # Only discovery should be called
        mock_clients["perplexity"].deep_research.assert_called_once()
        mock_clients["openai"].embed_text.assert_not_called()
        mock_clients["pinecone"].similarity_search.assert_not_called()
        mock_clients["openai"].chat_completion.assert_not_called()
        mock_clients["perplexity"].research.assert_not_called()

    @pytest.mark.slow
    def test_large_scale_pipeline(self, mock_clients, test_discovery_instructions):
        """Test pipeline with large number of events for performance."""
        # Discovery returns 10 events
        discovery_response = json.dumps(
            [{"title": f"Event {i}", "summary": f"Summary {i}"} for i in range(1, 11)]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # Deduplication: 3 duplicates filtered
        mock_clients["openai"].embed_text.side_effect = [
            [i * 0.1] * 1536 for i in range(1, 11)
        ]
        similarity_results = [[] for _ in range(7)]  # First 7 are unique
        similarity_results.extend([
            [("event_1", 0.85)],  # Event 8 similar to Event 1
            [("event_2", 0.85)],  # Event 9 similar to Event 2
            [("event_3", 0.85)],  # Event 10 similar to Event 3
        ])
        mock_clients["pinecone"].similarity_search.side_effect = similarity_results

        # Decision selects top 5 events
        mock_clients["openai"].chat_completion.return_value = "1, 2, 3, 4, 5"

        # Research processes 5 articles
        research_responses = [
            json.dumps({
                "headline": f"Article {i}",
                "summary": f"Summary {i}",
                "body": f"Story {i}",
                "sources": [f"https://source{i}.com"],
            })
            for i in range(1, 6)
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # Storage processes 5 articles
        mock_clients["mongodb"].insert_article.side_effect = [
            f"id{i}" for i in range(1, 6)
        ]

        with patch(
            "services.event_discovery.DISCOVERY_INSTRUCTIONS",
            test_discovery_instructions,
        ):
            events = discover_events(mock_clients["perplexity"])
            unique_events = deduplicate_events(
                events,
                openai_client=mock_clients["openai"],
                pinecone_client=mock_clients["pinecone"],
            )
            prioritized_events = select_events(
                unique_events, openai_client=mock_clients["openai"]
            )
            articles = research_articles(
                prioritized_events, perplexity_client=mock_clients["perplexity"]
            )

            # Store articles
            insert_articles(articles, mongodb_client=mock_clients["mongodb"])

        # Verify scale processing
        assert len(events) == 10
        assert len(unique_events) == 7  # 3 duplicates filtered
        assert len(prioritized_events) == 5  # Decision service selected top 5
        assert len(articles) == 5

        # Verify correct call counts
        assert mock_clients["openai"].embed_text.call_count == 10
        assert mock_clients["pinecone"].similarity_search.call_count == 10
        assert mock_clients["openai"].chat_completion.call_count == 1  # 1 decision
        assert mock_clients["perplexity"].research.call_count == 5
        assert mock_clients["mongodb"].insert_article.call_count == 5
