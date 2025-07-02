"""Integration tests for services pipeline."""

import json
from unittest.mock import Mock, patch

import pytest

from services import (
    deduplicate_events,
    discover_events,
    generate_audio,
    insert_articles,
    research_articles,
    select_events,
)
from utils import Article, Event


@pytest.mark.integration
class TestServicesIntegration:
    """Integration tests showing how services work together."""

    @pytest.fixture
    def test_discovery_instructions(self):
        """Test-specific discovery instructions with fixed date."""
        return (
            "Identify significant news about climate, environment and natural disasters, and major geopolitical events from today 2024-01-15. "
            "Focus on major global developments, breaking news, and important updates that would be of interest to a general audience. "
            "Return your findings as a JSON array of events, where each event has 'title' and 'summary' fields. "
            'Example format: [{"title": "Event Title", "summary": "Brief description..."}]'
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
        """Test complete pipeline from discovery to storage."""
        # Setup mock responses for each service

        # 1. Discovery Service Mock
        discovery_response = json.dumps(
            [
                {
                    "title": "Climate Summit 2024",
                    "summary": "World leaders gather to discuss urgent climate action plans.",
                },
                {
                    "title": "AI Breakthrough Announced",
                    "summary": "Revolutionary AI technology promises to transform healthcare.",
                },
            ]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # 2. Deduplication Service Mocks
        embeddings = [[0.1] * 1536, [0.2] * 1536]  # Two different embeddings
        mock_clients["openai"].embed_text.side_effect = embeddings
        mock_clients["pinecone"].similarity_search.return_value = (
            []
        )  # No duplicates found

        # 3. Decision Service Mocks
        mock_clients["openai"].chat_completion.return_value = (
            "1, 2"  # Select both events
        )

        # 4. Research Service Mocks
        research_responses = [
            json.dumps(
                {
                    "headline": "Global Climate Summit Sets Ambitious 2030 Targets",
                    "summary": "World leaders at the 2024 Climate Summit agreed on unprecedented carbon reduction goals.",
                    "story": "In a historic gathering of over 150 world leaders, the Climate Summit concluded with ambitious environmental commitments.",
                    "sources": [
                        "https://example.com/climate-summit",
                        "https://example.com/climate-targets",
                    ],
                }
            ),
            json.dumps(
                {
                    "headline": "AI Revolution in Healthcare Diagnostics",
                    "summary": "Breakthrough AI technology achieves 99% accuracy in medical diagnoses.",
                    "story": "Researchers have developed an revolutionary AI system that can diagnose diseases with unprecedented accuracy.",
                    "sources": [
                        "https://example.com/ai-healthcare",
                        "https://example.com/medical-ai",
                    ],
                }
            ),
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # 5. TTS Service Mocks
        mock_clients["openai"].chat_completion.side_effect = [
            "1, 2",  # Decision service response
            "Professional analysis of the climate summit developments for broadcast.",
            "Breaking news analysis of the AI breakthrough in healthcare technology.",
        ]
        mock_clients["openai"].text_to_speech.side_effect = [
            b"climate_summit_audio_data",
            b"ai_breakthrough_audio_data",
        ]
        mock_clients["mongodb"].insert_article.side_effect = [
            "60a1b2c3d4e5f6789",
            "60a1b2c3d4e5f6790",  # TTS service calls
            "60a1b2c3d4e5f6791",
            "60a1b2c3d4e5f6792",  # Storage service calls
        ]

        # Execute complete pipeline
        with (
            patch(
                "services.event_discovery.DISCOVERY_INSTRUCTIONS",
                test_discovery_instructions,
            ),
            patch(
                "services.audio_generation.get_random_REPORTER_VOICE",
                side_effect=[("ash", "Alex"), ("ballad", "Blake")],
            ),
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

            # 5. TTS Analysis & Broadcast Generation
            broadcast_articles = generate_audio(
                articles, openai_client=mock_clients["openai"]
            )

            # 6. Storage
            insert_articles(broadcast_articles, mongodb_client=mock_clients["mongodb"])

        # Verify pipeline results
        assert len(events) == 2
        assert len(unique_events) == 2  # No duplicates filtered
        assert len(prioritized_events) == 2  # Both events selected by decision service
        assert len(articles) == 2
        assert len(broadcast_articles) == 2

        # Verify data flow through pipeline
        # Events from discovery
        assert events[0].title == "Climate Summit 2024"
        assert events[1].title == "AI Breakthrough Announced"

        # Articles from research
        assert (
            articles[0].headline == "Global Climate Summit Sets Ambitious 2030 Targets"
        )
        assert articles[1].headline == "AI Revolution in Healthcare Diagnostics"
        assert articles[0].broadcast == b""  # Before TTS
        assert articles[1].broadcast == b""  # Before TTS

        # Articles after TTS
        assert broadcast_articles[0].broadcast == b"climate_summit_audio_data"
        assert broadcast_articles[1].broadcast == b"ai_breakthrough_audio_data"
        assert broadcast_articles[0].reporter == "Alex"
        assert broadcast_articles[1].reporter == "Blake"

        # Verify all clients were called
        mock_clients["perplexity"].deep_research.assert_called_once()
        assert mock_clients["openai"].embed_text.call_count == 2
        assert mock_clients["pinecone"].similarity_search.call_count == 2
        assert (
            mock_clients["openai"].chat_completion.call_count == 3
        )  # 1 decision + 2 TTS
        assert mock_clients["perplexity"].research.call_count == 2
        assert mock_clients["openai"].text_to_speech.call_count == 2
        # MongoDB called twice in storage service only = 2 total
        assert mock_clients["mongodb"].insert_article.call_count == 2

    def test_pipeline_with_deduplication(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline when duplicates are found and filtered."""
        # Discovery finds 3 events
        discovery_response = json.dumps(
            [
                {"title": "Event 1", "summary": "First event summary"},
                {"title": "Event 2", "summary": "Second event summary"},
                {"title": "Event 3", "summary": "Third event summary"},
            ]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # Deduplication finds Event 2 is duplicate
        embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]
        mock_clients["openai"].embed_text.side_effect = embeddings
        mock_clients["pinecone"].similarity_search.side_effect = [
            [],  # Event 1: no duplicates
            [("existing-event", 0.95)],  # Event 2: duplicate found
            [],  # Event 3: no duplicates
        ]

        # Research only processes 2 events (duplicate filtered out)
        research_responses = [
            json.dumps(
                {
                    "headline": "Event 1 Article",
                    "summary": "Article about event 1",
                    "story": "Full story about event 1",
                    "sources": ["https://example.com/event1"],
                }
            ),
            json.dumps(
                {
                    "headline": "Event 3 Article",
                    "summary": "Article about event 3",
                    "story": "Full story about event 3",
                    "sources": ["https://example.com/event3"],
                }
            ),
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # Decision selects remaining 2 events
        mock_clients["openai"].chat_completion.side_effect = [
            "1, 2",  # Decision service: select both remaining events
            "Analysis 1",
            "Analysis 2",  # TTS analyses
        ]

        # TTS processes 2 articles
        mock_clients["openai"].text_to_speech.side_effect = [b"audio1", b"audio3"]
        mock_clients["mongodb"].insert_article.side_effect = ["id1", "id3"]

        with (
            patch(
                "services.event_discovery.DISCOVERY_INSTRUCTIONS",
                test_discovery_instructions,
            ),
            patch(
                "services.audio_generation.get_random_REPORTER_VOICE",
                side_effect=[("ash", "Alex"), ("nova", "Nova")],
            ),
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
            broadcast_articles = generate_audio(
                articles, openai_client=mock_clients["openai"]
            )

            # Store the articles with broadcasts
            insert_articles(broadcast_articles, mongodb_client=mock_clients["mongodb"])

        # Verify deduplication worked
        assert len(events) == 3
        assert len(unique_events) == 2  # One duplicate filtered
        assert len(prioritized_events) == 2  # Decision kept both remaining events
        assert len(articles) == 2
        assert len(broadcast_articles) == 2

        # Verify correct events were kept
        assert unique_events[0].title == "Event 1"
        assert unique_events[1].title == "Event 3"
        # Event 2 should be filtered out by deduplication

        # Verify research only processed non-duplicate events
        assert mock_clients["perplexity"].research.call_count == 2

    def test_pipeline_error_handling_at_discovery(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline error handling when discovery fails."""
        mock_clients["perplexity"].deep_research.side_effect = Exception(
            "Discovery API failed"
        )

        with (
            patch(
                "services.event_discovery.DISCOVERY_INSTRUCTIONS",
                test_discovery_instructions,
            ),
            pytest.raises(Exception, match="Discovery API failed"),
        ):
            discover_events(mock_clients["perplexity"])

        # Subsequent services should not be called
        mock_clients["pinecone"].similarity_search.assert_not_called()
        mock_clients["perplexity"].research.assert_not_called()

    def test_pipeline_error_handling_at_research(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline error handling when research fails."""
        # Discovery succeeds
        discovery_response = json.dumps(
            [{"title": "Event 1", "summary": "Event summary"}]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # Deduplication succeeds
        mock_clients["openai"].embed_text.return_value = [0.1] * 1536
        mock_clients["pinecone"].similarity_search.return_value = []

        # Research fails
        mock_clients["perplexity"].research.side_effect = Exception(
            "Research API failed"
        )

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

            with pytest.raises(Exception, match="Research API failed"):
                research_articles(
                    unique_events, perplexity_client=mock_clients["perplexity"]
                )

        # Verify services up to failure point were called
        mock_clients["perplexity"].deep_research.assert_called_once()
        mock_clients["pinecone"].similarity_search.assert_called_once()
        mock_clients["perplexity"].research.assert_called_once()

        # TTS should not be called
        mock_clients["openai"].chat_completion.assert_not_called()

    def test_pipeline_partial_tts_failure(
        self, mock_clients, test_discovery_instructions
    ):
        """Test pipeline when some articles fail in TTS processing."""
        # Setup successful discovery, deduplication, and research
        discovery_response = json.dumps(
            [
                {"title": "Event 1", "summary": "Event 1 summary"},
                {"title": "Event 2", "summary": "Event 2 summary"},
            ]
        )
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        mock_clients["openai"].embed_text.side_effect = [[0.1] * 1536, [0.2] * 1536]
        mock_clients["pinecone"].similarity_search.return_value = []

        # Decision: Select both events
        decision_and_tts_responses = [
            "1, 2",  # Decision service: select both events
            "Analysis 1",
            Exception("TTS failed for second article"),
        ]

        research_responses = [
            json.dumps(
                {
                    "headline": "Article 1",
                    "summary": "Summary 1",
                    "story": "Story 1",
                    "sources": ["https://example.com/1"],
                }
            ),
            json.dumps(
                {
                    "headline": "Article 2",
                    "summary": "Summary 2",
                    "story": "Story 2",
                    "sources": ["https://example.com/2"],
                }
            ),
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # TTS: First article succeeds, second fails (including decision service call)
        mock_clients["openai"].chat_completion.side_effect = decision_and_tts_responses
        mock_clients["openai"].text_to_speech.side_effect = [b"audio1"]
        mock_clients["mongodb"].insert_article.side_effect = ["id1"]

        with (
            patch(
                "services.event_discovery.DISCOVERY_INSTRUCTIONS",
                test_discovery_instructions,
            ),
            patch(
                "services.audio_generation.get_random_REPORTER_VOICE",
                side_effect=[("ash", "Alex")],
            ),
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

            # TTS processing with partial failure
            broadcast_articles = generate_audio(
                articles, openai_client=mock_clients["openai"]
            )

            # Store successfully processed articles
            if broadcast_articles:
                insert_articles(
                    broadcast_articles, mongodb_client=mock_clients["mongodb"]
                )

        # Should have 2 articles going into TTS, 1 coming out (due to failure)
        assert len(articles) == 2
        assert len(broadcast_articles) == 1
        assert broadcast_articles[0].headline == "Article 1"
        assert broadcast_articles[0].broadcast == b"audio1"
        assert broadcast_articles[0].reporter == "Alex"

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
        mock_clients["openai"].chat_completion.side_effect = [
            "1",  # Decision service: select first event
            "Professional broadcast analysis",  # TTS service
        ]

        # Research: Processes Event objects, returns Article objects
        research_response = json.dumps(
            {
                "headline": "Transformed Headline",
                "summary": "Transformed summary with more detail",
                "story": "Full story with comprehensive details about the original event",
                "sources": [
                    "https://example.com/source1",
                    "https://example.com/source2",
                ],
            }
        )
        mock_clients["perplexity"].research.return_value = research_response

        # TTS: Processes Article objects, returns Article objects with broadcast data
        mock_clients["openai"].text_to_speech.return_value = b"final_audio_data"
        mock_clients["mongodb"].insert_article.return_value = "final_id"

        with (
            patch(
                "services.event_discovery.DISCOVERY_INSTRUCTIONS",
                test_discovery_instructions,
            ),
            patch(
                "services.audio_generation.get_random_REPORTER_VOICE",
                return_value=("ballad", "Blake"),
            ),
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
            final_articles = generate_audio(
                articles, openai_client=mock_clients["openai"]
            )

            # Store final articles
            insert_articles(final_articles, mongodb_client=mock_clients["mongodb"])

        # Verify data transformations
        # Event -> Event (deduplication preserves structure)
        assert isinstance(events[0], Event)
        assert isinstance(unique_events[0], Event)
        assert events[0].title == unique_events[0].title

        # Event -> Event (decision preserves structure, filters by impact)
        assert isinstance(prioritized_events[0], Event)
        assert prioritized_events[0].title == unique_events[0].title

        # Event -> Article (research transforms and enhances)
        assert isinstance(articles[0], Article)
        assert articles[0].headline == "Transformed Headline"
        assert (
            articles[0].summary != prioritized_events[0].summary
        )  # Enhanced by research
        assert len(articles[0].sources) == 2
        assert articles[0].broadcast == b""  # Empty before TTS
        assert articles[0].reporter == ""  # Empty before TTS

        # Article -> Article (TTS adds broadcast data)
        assert isinstance(final_articles[0], Article)
        assert final_articles[0].headline == articles[0].headline  # Preserved
        assert final_articles[0].summary == articles[0].summary  # Preserved
        assert final_articles[0].story == articles[0].story  # Preserved
        assert final_articles[0].sources == articles[0].sources  # Preserved
        assert final_articles[0].broadcast == b"final_audio_data"  # Added by TTS
        assert final_articles[0].reporter == "Blake"  # Added by TTS

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

            broadcast_articles = generate_audio(
                articles, openai_client=mock_clients["openai"]
            )

        # All results should be empty
        assert events == []
        assert unique_events == []
        assert articles == []
        assert broadcast_articles == []

        # Only discovery should be called
        mock_clients["perplexity"].deep_research.assert_called_once()
        mock_clients["openai"].embed_text.assert_not_called()
        mock_clients["pinecone"].similarity_search.assert_not_called()
        mock_clients["perplexity"].research.assert_not_called()
        mock_clients["openai"].chat_completion.assert_not_called()

    @pytest.mark.slow
    def test_large_scale_pipeline(self, mock_clients, test_discovery_instructions):
        """Test pipeline with larger data volumes."""
        # Generate 10 events
        events_data = [
            {"title": f"Event {i}", "summary": f"Summary for event {i}"}
            for i in range(10)
        ]
        discovery_response = json.dumps(events_data)
        mock_clients["perplexity"].deep_research.return_value = discovery_response

        # Deduplication: Filter out 3 events as duplicates
        embeddings = [[i * 0.1] * 1536 for i in range(10)]
        mock_clients["openai"].embed_text.side_effect = embeddings
        similarity_results = [
            [],  # 0: no duplicates
            [],  # 1: no duplicates
            [("dup", 0.9)],  # 2: duplicate
            [],  # 3: no duplicates
            [],  # 4: no duplicates
            [("dup", 0.85)],  # 5: duplicate
            [],  # 6: no duplicates
            [],  # 7: no duplicates
            [("dup", 0.92)],  # 8: duplicate
            [],  # 9: no duplicates
        ]
        mock_clients["pinecone"].similarity_search.side_effect = similarity_results

        # Decision: Select top 5 events from the 7 unique events
        mock_clients["openai"].chat_completion.side_effect = [
            "1, 2, 3, 4, 5",  # Decision service: select first 5 events
            *[f"Analysis {i}" for i in range(5)],  # TTS analyses for 5 selected events
        ]

        # Research: Process 5 selected events
        research_responses = [
            json.dumps(
                {
                    "headline": f"Article {i}",
                    "summary": f"Article summary {i}",
                    "story": f"Article story {i}",
                    "sources": [f"https://example.com/{i}"],
                }
            )
            for i in range(5)  # First 5 events selected by decision service
        ]
        mock_clients["perplexity"].research.side_effect = research_responses

        # TTS: Process 5 articles successfully
        mock_clients["openai"].text_to_speech.side_effect = [
            f"audio_{i}".encode() for i in range(5)
        ]
        mock_clients["mongodb"].insert_article.side_effect = [
            f"id_{i}" for i in range(5)
        ]

        with (
            patch(
                "services.event_discovery.DISCOVERY_INSTRUCTIONS",
                test_discovery_instructions,
            ),
            patch(
                "services.audio_generation.get_random_REPORTER_VOICE",
                side_effect=[("ash", "Alex")] * 5,
            ),
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
            broadcast_articles = generate_audio(
                articles, openai_client=mock_clients["openai"]
            )

            # Store articles if any were processed
            if broadcast_articles:
                insert_articles(
                    broadcast_articles, mongodb_client=mock_clients["mongodb"]
                )

        # Verify scale processing
        assert len(events) == 10
        assert len(unique_events) == 7  # 3 duplicates filtered
        assert len(prioritized_events) == 5  # Decision service selected top 5
        assert len(articles) == 5
        assert len(broadcast_articles) == 5

        # Verify correct call counts
        assert mock_clients["openai"].embed_text.call_count == 10
        assert mock_clients["pinecone"].similarity_search.call_count == 10
        assert (
            mock_clients["openai"].chat_completion.call_count == 6
        )  # 1 decision + 5 TTS
        assert mock_clients["perplexity"].research.call_count == 5
        assert mock_clients["openai"].text_to_speech.call_count == 5
