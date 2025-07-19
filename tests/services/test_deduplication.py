"""Test suite for deduplication service."""

from unittest.mock import Mock, patch

import pytest

from models import Lead
from services import deduplicate_leads


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
    def sample_leads(self):
        """Sample leads for testing."""
        return [
            Lead(
                tip="Climate Summit 2024: World leaders meet to discuss climate "
                "change solutions and carbon reduction targets.",
            ),
            Lead(
                tip="Earthquake in Pacific: A 6.5 magnitude earthquake struck the "
                "Pacific region with minimal damage reported.",
            ),
            Lead(
                tip="Tech Conference Announced: Major technology companies "
                "announce new AI developments at annual conference.",
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

    def test_deduplicate_leads_no_duplicates(
        self, sample_leads, sample_embeddings, mock_openai_client, mock_pinecone_client
    ):
        """Test deduplication when no duplicates exist."""
        # Setup mocks
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.return_value = []  # No duplicates

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # Verify results
        assert len(result) == 3
        assert result == sample_leads

        # Verify embedding calls
        assert mock_openai_client.embed_text.call_count == 3
        mock_openai_client.embed_text.assert_any_call(sample_leads[0].tip)
        mock_openai_client.embed_text.assert_any_call(sample_leads[1].tip)
        mock_openai_client.embed_text.assert_any_call(sample_leads[2].tip)

        # Verify upsert calls
        assert mock_pinecone_client.upsert_vector.call_count == 3

    def test_deduplicate_leads_with_duplicates(
        self, sample_leads, sample_embeddings, mock_openai_client, mock_pinecone_client
    ):
        """Test deduplication when duplicates exist."""
        # Setup mocks - second lead is a duplicate
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.side_effect = [
            [],  # First lead - no duplicates
            [("existing-id", 0.95)],  # Second lead - duplicate found
            [],  # Third lead - no duplicates
        ]

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # Verify results - should skip the duplicate (second lead)
        assert len(result) == 2
        assert result[0] == sample_leads[0]
        assert result[1] == sample_leads[2]

        # Verify only 2 vectors were upserted (excluding duplicate)
        assert mock_pinecone_client.upsert_vector.call_count == 2

    def test_deduplicate_leads_empty_input(
        self, mock_openai_client, mock_pinecone_client
    ):
        """Test deduplication with empty input."""
        result = deduplicate_leads(
            [],
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        assert result == []
        assert mock_openai_client.embed_text.call_count == 0
        assert mock_pinecone_client.upsert_vector.call_count == 0

    @patch("services.lead_deduplication.logger")
    def test_logging_duplicate_detection(
        self,
        mock_logger,
        sample_leads,
        sample_embeddings,
        mock_openai_client,
        mock_pinecone_client,
    ):
        """Test that deduplication completion is logged."""
        # Setup mocks
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.side_effect = [
            [],  # First lead - no duplicates
            [("existing-id", 0.95)],  # Second lead - duplicate found
            [],  # Third lead - no duplicates
        ]

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # Verify that duplicates were properly filtered out
        assert len(result) == 2  # Should have 2 unique leads (skipping the duplicate)

        # Verify completion logging - updated to match new emoji-based format
        mock_logger.info.assert_any_call("  🔄 Removed %d duplicate leads", 1)

    def test_vector_metadata_structure(
        self, sample_leads, sample_embeddings, mock_openai_client, mock_pinecone_client
    ):
        """Test that vectors are stored with correct metadata."""
        # Setup mocks
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.return_value = []

        # Call function
        deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
        )

        # Verify metadata for each upsert call
        calls = mock_pinecone_client.upsert_vector.call_args_list

        for i, call in enumerate(calls):
            args, kwargs = call
            vector_id, vector = args
            metadata = kwargs["metadata"]
            assert vector_id == f"lead-{i}"
            assert vector == sample_embeddings[i]
            assert metadata["tip"] == sample_leads[i].tip
            assert metadata["date"] == sample_leads[i].date
