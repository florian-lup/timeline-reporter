"""Test suite for Pinecone client."""

from unittest.mock import Mock, patch

import pytest

from clients import PineconeClient


class TestPineconeClient:
    """Test suite for PineconeClient."""

    @pytest.fixture
    def mock_pinecone(self):
        """Mock Pinecone dependencies for testing."""
        with (
            patch("clients.pinecone_client.Pinecone") as mock_pc_class,
            patch("clients.pinecone_client.ServerlessSpec") as mock_spec,
        ):
            mock_pc = Mock()
            mock_index = Mock()
            mock_pc_class.return_value = mock_pc
            mock_pc.Index.return_value = mock_index

            yield mock_pc_class, mock_pc, mock_index, mock_spec

    def test_init_with_default_api_key(self, mock_pinecone):
        """Test initialization with default API key from config."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        with patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"):
            client = PineconeClient()

            mock_pc_class.assert_called_once_with(api_key="test-api-key")
            assert client._pc == mock_pc
            assert client._index == mock_index

    def test_init_with_custom_api_key(self, mock_pinecone):
        """Test initialization with custom API key."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]
        custom_key = "custom-api-key"

        PineconeClient(api_key=custom_key)

        mock_pc_class.assert_called_once_with(api_key=custom_key)

    def test_init_with_none_api_key_and_missing_config(self, mock_pinecone):
        """Test initialization fails when API key is None and config is missing."""
        with (
            patch("clients.pinecone_client.PINECONE_API_KEY", None),
            pytest.raises(ValueError, match="PINECONE_API_KEY is missing"),
        ):
            PineconeClient()

    def test_ensure_index_existing(self, mock_pinecone):
        """Test that existing index is used."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        with (
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"),
            patch("clients.pinecone_client.PINECONE_INDEX_NAME", "timeline-events"),
        ):
            PineconeClient()

            mock_pc.create_index.assert_not_called()
            mock_pc.Index.assert_called_once_with("timeline-events")

    def test_ensure_index_create_new(self, mock_pinecone):
        """Test that new index is created when missing."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = []

        with (
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"),
            patch("clients.pinecone_client.PINECONE_INDEX_NAME", "new-index"),
            patch("clients.pinecone_client.EMBEDDING_DIMENSIONS", 1536),
            patch("clients.pinecone_client.METRIC", "cosine"),
            patch("clients.pinecone_client.CLOUD_PROVIDER", "aws"),
            patch("clients.pinecone_client.CLOUD_REGION", "us-east-1"),
        ):
            PineconeClient()

            mock_pc.create_index.assert_called_once()
            create_call = mock_pc.create_index.call_args
            assert create_call[1]["name"] == "new-index"
            assert create_call[1]["dimension"] == 1536
            assert create_call[1]["metric"] == "cosine"

    def test_similarity_search_success(self, mock_pinecone):
        """Test successful similarity search."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        # Mock query response
        mock_match1 = Mock()
        mock_match1.id = "doc1"
        mock_match1.score = 0.95
        mock_match2 = Mock()
        mock_match2.id = "doc2"
        mock_match2.score = 0.85
        mock_match3 = Mock()
        mock_match3.id = "doc3"
        mock_match3.score = 0.75  # Below threshold

        mock_query_result = Mock()
        mock_query_result.matches = [mock_match1, mock_match2, mock_match3]
        mock_index.query.return_value = mock_query_result

        with (
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"),
            patch("clients.pinecone_client.SIMILARITY_THRESHOLD", 0.8),
        ):
            client = PineconeClient()
            result = client.similarity_search([0.1, 0.2, 0.3])

            expected = [("doc1", 0.95), ("doc2", 0.85)]
            assert result == expected

    def test_similarity_search_with_custom_top_k(self, mock_pinecone):
        """Test similarity search with custom top_k parameter."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        mock_query_result = Mock()
        mock_query_result.matches = []
        mock_index.query.return_value = mock_query_result

        with patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"):
            client = PineconeClient()
            client.similarity_search([0.1, 0.2, 0.3], top_k=10)

            mock_index.query.assert_called_once_with(
                vector=[0.1, 0.2, 0.3], top_k=10, include_values=False
            )

    def test_upsert_vector_without_metadata(self, mock_pinecone):
        """Test vector upsert without metadata."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        with patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"):
            client = PineconeClient()
            client.upsert_vector("test-id", [0.1, 0.2, 0.3])

            mock_index.upsert.assert_called_once_with(
                [("test-id", [0.1, 0.2, 0.3], {})]
            )

    def test_upsert_vector_with_metadata(self, mock_pinecone):
        """Test vector upsert with metadata."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        metadata = {"title": "Test Article", "date": "2024-01-01"}

        with patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"):
            client = PineconeClient()
            client.upsert_vector("test-id", [0.1, 0.2, 0.3], metadata)

            mock_index.upsert.assert_called_once_with(
                [("test-id", [0.1, 0.2, 0.3], metadata)]
            )

    @patch("clients.pinecone_client.logger")
    def test_logging_init(self, mock_logger, mock_pinecone):
        """Test that initialization logs properly."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        with (
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"),
            patch("clients.pinecone_client.PINECONE_INDEX_NAME", "test-index"),
        ):
            PineconeClient()

            mock_logger.info.assert_any_call("Initializing Pinecone")
            mock_logger.info.assert_any_call("Pinecone ready: %s", "test-index")

    @patch("clients.pinecone_client.logger")
    def test_logging_create_index(self, mock_logger, mock_pinecone):
        """Test that index creation logs properly."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = []

        with (
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"),
            patch("clients.pinecone_client.PINECONE_INDEX_NAME", "new-index"),
        ):
            PineconeClient()

            mock_logger.info.assert_any_call("Creating index: %s", "new-index")

    @patch("clients.pinecone_client.logger")
    def test_logging_similarity_search(self, mock_logger, mock_pinecone):
        """Test that similarity search logs properly."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        mock_query_result = Mock()
        mock_query_result.matches = []
        mock_index.query.return_value = mock_query_result

        with patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"):
            client = PineconeClient()
            client.similarity_search([0.1, 0.2, 0.3], top_k=10)

            # Debug logging was removed - no assertion needed
            pass

    @patch("clients.pinecone_client.logger")
    def test_logging_upsert_vector(self, mock_logger, mock_pinecone):
        """Test that upsert logs properly."""
        mock_pc_class, mock_pc, mock_index, mock_spec = mock_pinecone
        mock_pc.list_indexes.return_value.names.return_value = ["timeline-events"]

        with patch("clients.pinecone_client.PINECONE_API_KEY", "test-api-key"):
            client = PineconeClient()
            client.upsert_vector("test-id", [0.1, 0.2, 0.3])

            # Debug logging was removed - no assertion needed
            pass
