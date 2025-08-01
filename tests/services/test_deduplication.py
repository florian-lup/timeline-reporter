"""Test suite for deduplication service."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Lead
from services import deduplicate_leads
from services.lead_deduplication import _compare_with_database_records


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
    def mock_mongodb_client(self):
        """Mock MongoDB client for testing."""
        return Mock()

    @pytest.fixture
    def sample_leads(self):
        """Sample leads for testing."""
        return [
            Lead(
                discovered_lead="Climate Summit 2024: World leaders meet to discuss climate change solutions and carbon reduction targets.",
            ),
            Lead(
                discovered_lead="Earthquake in Pacific: A 6.5 magnitude earthquake struck the Pacific region with minimal damage reported.",
            ),
            Lead(
                discovered_lead="Tech Conference Announced: Major technology companies announce new AI developments at annual conference.",
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
        self,
        sample_leads,
        sample_embeddings,
        mock_openai_client,
        mock_pinecone_client,
        mock_mongodb_client,
    ):
        """Test deduplication when no duplicates exist."""
        # Setup mocks
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.return_value = []  # No duplicates
        mock_mongodb_client.get_recent_stories.return_value = []  # No recent stories

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
            mongodb_client=mock_mongodb_client,
        )

        # Verify results
        assert len(result) == 3
        assert result == sample_leads

        # Verify embedding calls
        assert mock_openai_client.embed_text.call_count == 3
        mock_openai_client.embed_text.assert_any_call(sample_leads[0].discovered_lead)
        mock_openai_client.embed_text.assert_any_call(sample_leads[1].discovered_lead)
        mock_openai_client.embed_text.assert_any_call(sample_leads[2].discovered_lead)

        # Verify upsert calls
        assert mock_pinecone_client.upsert_vector.call_count == 3

    def test_deduplicate_leads_with_duplicates(
        self,
        sample_leads,
        sample_embeddings,
        mock_openai_client,
        mock_pinecone_client,
        mock_mongodb_client,
    ):
        """Test deduplication when duplicates exist."""
        # Setup mocks - second lead is a duplicate
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.side_effect = [
            [],  # First lead - no duplicates
            [("existing-id", 0.95)],  # Second lead - duplicate found
            [],  # Third lead - no duplicates
        ]
        mock_mongodb_client.get_recent_stories.return_value = []  # No recent stories

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
            mongodb_client=mock_mongodb_client,
        )

        # Verify results - should skip the duplicate (second lead)
        assert len(result) == 2
        assert result[0] == sample_leads[0]
        assert result[1] == sample_leads[2]

        # Verify only 2 vectors were upserted (excluding duplicate)
        assert mock_pinecone_client.upsert_vector.call_count == 2

    def test_deduplicate_leads_empty_input(self, mock_openai_client, mock_pinecone_client, mock_mongodb_client):
        """Test deduplication with empty input."""
        result = deduplicate_leads(
            [],
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
            mongodb_client=mock_mongodb_client,
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
        mock_mongodb_client,
    ):
        """Test that deduplication completion is logged."""
        # Setup mocks
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.side_effect = [
            [],  # First lead - no duplicates
            [("existing-id", 0.95)],  # Second lead - duplicate found
            [],  # Third lead - no duplicates
        ]

        # Setup mock
        mock_mongodb_client.get_recent_stories.return_value = []  # No recent stories

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
            mongodb_client=mock_mongodb_client,
        )

        # Verify that duplicates were properly filtered out
        assert len(result) == 2  # Should have 2 unique leads (skipping the duplicate)

        # Verify completion logging - updated to match new emoji-based format
        mock_logger.info.assert_any_call("  🔄 Vector layer: Removed %d duplicates", 1)

    def test_vector_metadata_structure(
        self,
        sample_leads,
        sample_embeddings,
        mock_openai_client,
        mock_pinecone_client,
        mock_mongodb_client,
    ):
        """Test that vectors are stored with correct metadata."""
        # Setup mocks
        mock_openai_client.embed_text.side_effect = sample_embeddings
        mock_pinecone_client.similarity_search.return_value = []
        mock_mongodb_client.get_recent_stories.return_value = []  # No recent stories

        # Call function
        deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
            mongodb_client=mock_mongodb_client,
        )

        # Verify metadata for each upsert call
        calls = mock_pinecone_client.upsert_vector.call_args_list

        for i, call in enumerate(calls):
            args, kwargs = call
            vector_id, vector = args
            metadata = kwargs["metadata"]
            assert vector_id == f"lead-{i}"
            assert vector == sample_embeddings[i]
            assert metadata["discovered_lead"] == sample_leads[i].discovered_lead
            assert metadata["date"] == sample_leads[i].date

    def test_database_deduplication_with_duplicates(self, sample_leads, mock_openai_client, mock_pinecone_client, mock_mongodb_client):
        """Test database deduplication when duplicates exist."""
        # Setup mocks for vector layer - pass all leads
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.return_value = []

        # Setup recent stories in database with similar content
        mock_mongodb_client.get_recent_stories.return_value = [
            {"summary": "World leaders meet at Climate Summit 2024 to discuss global climate goals."}
        ]

        # Setup GPT response to identify first lead as duplicate
        gpt_response = json.dumps({"result": "DUPLICATE"})
        mock_openai_client.chat_completion.side_effect = [
            gpt_response,  # First lead - duplicate
            json.dumps({"result": "UNIQUE"}),  # Second lead - unique
            json.dumps({"result": "UNIQUE"}),  # Third lead - unique
        ]

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
            mongodb_client=mock_mongodb_client,
        )

        # Verify results - should have filtered out the first lead
        assert len(result) == 2
        assert sample_leads[0] not in result
        assert sample_leads[1] in result
        assert sample_leads[2] in result

        # Verify chat completion calls
        assert mock_openai_client.chat_completion.call_count == 3

    def test_database_deduplication_no_recent_stories(self, sample_leads, mock_openai_client, mock_pinecone_client, mock_mongodb_client):
        """Test database deduplication with no recent stories."""
        # Setup mocks
        mock_openai_client.embed_text.return_value = [0.1] * 1536
        mock_pinecone_client.similarity_search.return_value = []
        mock_mongodb_client.get_recent_stories.return_value = []  # No recent stories

        # Call function
        result = deduplicate_leads(
            sample_leads,
            openai_client=mock_openai_client,
            pinecone_client=mock_pinecone_client,
            mongodb_client=mock_mongodb_client,
        )

        # All leads should pass through without database deduplication
        assert len(result) == 3
        assert result == sample_leads

        # Verify no chat completion calls
        mock_openai_client.chat_completion.assert_not_called()

    def test_compare_with_database_records(self, mock_openai_client):
        """Test the _compare_with_database_records helper function."""
        lead = Lead(discovered_lead="Test lead about important news")
        recent_stories: list[dict[str, object]] = [
            {"summary": "Summary about test news"},
            {"summary": "Another summary about different topic"},
        ]

        # Mock GPT response indicating duplicate
        mock_openai_client.chat_completion.return_value = json.dumps({"result": "DUPLICATE"})

        # Call function
        result = _compare_with_database_records(lead, recent_stories, mock_openai_client)

        # Should be identified as duplicate
        assert result is True

        # Verify chat completion was called
        mock_openai_client.chat_completion.assert_called_once()

    def test_compare_with_database_records_empty(self, mock_openai_client):
        """Test _compare_with_database_records with empty recent stories."""
        lead = Lead(discovered_lead="Test lead about important news")

        # Call function with empty stories
        result = _compare_with_database_records(lead, [], mock_openai_client)

        # Should not be a duplicate
        assert result is False

        # Verify no chat completion calls
        mock_openai_client.chat_completion.assert_not_called()

    def test_compare_with_database_records_exception(self, mock_openai_client):
        """Test error handling in _compare_with_database_records."""
        lead = Lead(discovered_lead="Test lead about important news")
        recent_stories: list[dict[str, object]] = [{"summary": "Test summary"}]

        # Mock error in chat completion
        mock_openai_client.chat_completion.side_effect = Exception("API error")

        # Verify exception is raised
        with pytest.raises(RuntimeError, match="GPT database comparison failed: API error"):
            _compare_with_database_records(lead, recent_stories, mock_openai_client)
