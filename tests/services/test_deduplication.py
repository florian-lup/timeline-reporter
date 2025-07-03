"""Test suite for deduplication service."""

from unittest.mock import Mock, patch

import pytest

from services import deduplicate_events
from utils import Event


class TestDeduplicationService:
    """Test suite for deduplication service functions."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        return Mock()

    @pytest.fixture
    def mock_pinecone_client(self):
        """Mock Pinecone client for testing."""
        return Mock()

    @pytest.fixture
    def sample_events(self):
        """Sample events for testing."""
        return [
            Event(
                title="Climate Summit 2024",
                summary=(
                    "World leaders meet to discuss climate change solutions and "
                    "carbon reduction targets."
                ),
            ),
            Event(
                title="Earthquake in Pacific",
                summary=(
                    "A 6.5 magnitude earthquake struck the Pacific region with "
                    "minimal damage reported."
                ),
            ),
            Event(
                title="Tech Conference Announced",
                summary=(
                    "Major technology companies announce new AI developments at "
                    "annual conference."
                ),
            ),
        ]

    @pytest.fixture
    def sample_embeddings(self):
        """Sample embeddings for testing."""
        return [
            [0.1, 0.2, 0.3] * 512,  # 1536 dimensions
            [0.4, 0.5, 0.6] * 512,
            [0.7, 0.8, 0.9] * 512,
        ]

    def test_deduplicate_events_no_duplicates(
        self, mock_openai_client, mock_pinecone_client, sample_events, sample_embeddings
    ):
        """Test deduplication when no duplicates exist."""
        # Setup mocks
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.return_value = []  # No matches found

        result = deduplicate_events(
            sample_events,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # All events should be kept
        assert len(result) == 3
        assert result == sample_events

        # Verify embeddings were created for all events
        assert mock_openai_client.embed_text.call_count == 3

        # Verify similarity searches were performed
        assert mock_pinecone_client.similarity_search.call_count == 3

        # Verify vectors were upserted for all events
        assert mock_pinecone_client.upsert_vector.call_count == 3

    def test_deduplicate_events_with_duplicates(
        self, mock_openai_client, mock_pinecone_client, sample_events, sample_embeddings
    ):
        """Test deduplication when duplicates exist."""
        # Setup mocks - second event has duplicates
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.side_effect = [
            [],  # First event: no duplicates
            [("existing-event-1", 0.95)],  # Second event: has duplicate
            [],  # Third event: no duplicates
        ]

        with patch("services.event_deduplication.logger") as mock_logger:
            result = deduplicate_events(
                sample_events,
                openai_client=mock_openai_client,
                pinecone_client=mock_pinecone_client,
            )

        # Only 2 events should remain (duplicate removed)
        assert len(result) == 2
        assert result[0] == sample_events[0]  # First event kept
        assert result[1] == sample_events[2]  # Third event kept

        # Verify duplicate was logged
        mock_logger.info.assert_any_call(
            "Skipping duplicate: '%s' (similarity: %.2f)", sample_events[1].title, 0.95
        )

        # Only 2 vectors should be upserted (not the duplicate)
        assert mock_pinecone_client.upsert_vector.call_count == 2

    def test_deduplicate_events_embedding_content(
        self, mock_openai_client, mock_pinecone_client, sample_events
    ):
        """Test that embeddings use correct text content."""
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.return_value = []

        deduplicate_events(
            sample_events,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # Verify embedding text combines title and summary
        embedding_calls = mock_openai_client.embed_text.call_args_list
        assert len(embedding_calls) == 3

        expected_text_0 = sample_events[0].title + "\n" + sample_events[0].summary
        expected_text_1 = sample_events[1].title + "\n" + sample_events[1].summary
        expected_text_2 = sample_events[2].title + "\n" + sample_events[2].summary

        assert embedding_calls[0][0][0] == expected_text_0
        assert embedding_calls[1][0][0] == expected_text_1
        assert embedding_calls[2][0][0] == expected_text_2

    def test_deduplicate_events_vector_metadata(
        self, mock_openai_client, mock_pinecone_client, sample_events
    ):
        """Test that vectors are upserted with correct metadata."""
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.return_value = []

        deduplicate_events(
            sample_events,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # Verify upsert calls have correct metadata
        upsert_calls = mock_pinecone_client.upsert_vector.call_args_list
        assert len(upsert_calls) == 3

        for i, call in enumerate(upsert_calls):
            args, kwargs = call
            vector_id, vector = args
            metadata = kwargs["metadata"]
            assert vector_id == f"event-{i}"
            assert vector == [0.1] * 1536
            assert metadata["title"] == sample_events[i].title
            assert metadata["summary"] == sample_events[i].summary

    def test_deduplicate_events_empty_list(
        self, mock_openai_client, mock_pinecone_client
    ):
        """Test deduplication with empty event list."""
        with patch("services.event_deduplication.logger") as mock_logger:
            result = deduplicate_events(
                [],
                openai_client=mock_openai_client,
                pinecone_client=mock_pinecone_client,
            )

        assert result == []
        mock_openai_client.embed_text.assert_not_called()
        mock_pinecone_client.similarity_search.assert_not_called()
        mock_pinecone_client.upsert_vector.assert_not_called()

        mock_logger.info.assert_called_with(
            "Deduplication complete: %d unique events", 0
        )

    def test_deduplicate_events_single_event(
        self, mock_openai_client, mock_pinecone_client
    ):
        """Test deduplication with single event."""
        single_event = [Event(title="Solo Event", summary="Only event in list")]
        mock_openai_client.embed_text.return_value = [0.5] * 1536
        mock_pinecone_client.similarity_search.return_value = []

        result = deduplicate_events(
            single_event,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        assert len(result) == 1
        assert result[0] == single_event[0]

    def test_deduplicate_events_multiple_matches(
        self, mock_openai_client, mock_pinecone_client, sample_events
    ):
        """Test deduplication when event matches multiple existing events."""
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.side_effect = [
            [
                ("match-1", 0.95),
                ("match-2", 0.88),
                ("match-3", 0.82),
            ],  # Multiple matches
            [],  # No duplicates
            [],  # No duplicates
        ]

        with patch("services.event_deduplication.logger") as mock_logger:
            result = deduplicate_events(
                sample_events,
                openai_client=mock_openai_client,
                pinecone_client=mock_pinecone_client,
            )

        # First event should be skipped due to multiple matches
        assert len(result) == 2
        assert result[0] == sample_events[1]
        assert result[1] == sample_events[2]

        # Verify logging shows multiple matches
        mock_logger.info.assert_any_call(
            "Skipping duplicate: '%s' (similarity: %.2f)",
            sample_events[0].title,
            0.95,  # Best score
        )

    @pytest.mark.parametrize(
        "similarity_scores",
        [
            [("match-1", 0.85)],  # Above threshold
            [("match-1", 0.95), ("match-2", 0.90)],  # Multiple above threshold
            [("match-1", 0.99)],  # Very high similarity
        ],
    )
    def test_deduplicate_events_various_similarity_scores(
        self, mock_openai_client, mock_pinecone_client, sample_events, similarity_scores
    ):
        """Test deduplication with various similarity scores."""
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.side_effect = [
            similarity_scores,  # First event has matches
            [],  # Second event no matches
            [],  # Third event no matches
        ]

        result = deduplicate_events(
            sample_events,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # First event should be filtered out due to similarity
        assert len(result) == 2
        assert sample_events[0] not in result

    @patch("services.event_deduplication.logger")
    def test_logging_deduplication(
        self, mock_logger, mock_openai_client, mock_pinecone_client, sample_events
    ):
        """Test that deduplication logs properly."""
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.return_value = []

        deduplicate_events(
            sample_events,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        mock_logger.info.assert_called_with(
            "Deduplication complete: %d unique events", 3
        )

    def test_deduplicate_events_embedding_error_handling(
        self, mock_openai_client, mock_pinecone_client, sample_events
    ):
        """Test error handling when embedding fails."""
        # First embedding succeeds, second fails
        mock_openai_client.embed_text.side_effect = [
            [0.1] * 1536,
            Exception("Embedding failed"),
        ]
        mock_pinecone_client.similarity_search.return_value = (
            []
        )  # No matches for first event

        # Should propagate the exception
        with pytest.raises(Exception, match="Embedding failed"):
            deduplicate_events(
                sample_events,
                openai_client=mock_openai_client,
                pinecone_client=mock_pinecone_client,
            )

    def test_deduplicate_events_search_error_handling(
        self, mock_openai_client, mock_pinecone_client, sample_events
    ):
        """Test error handling when similarity search fails."""
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.side_effect = Exception("Search failed")

        # Should propagate the exception
        with pytest.raises(Exception, match="Search failed"):
            deduplicate_events(
                sample_events,
                openai_client=mock_openai_client,
                pinecone_client=mock_pinecone_client,
            )
