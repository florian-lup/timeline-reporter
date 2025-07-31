"""Test suite for MongoDB client."""

from unittest.mock import Mock, patch

import pytest
from bson import ObjectId

from clients import MongoDBClient


class TestMongoDBClient:
    """Test suite for MongoDBClient."""

    @pytest.fixture
    def mock_mongo_client(self):
        """Mock pymongo.MongoClient."""
        with patch("clients.mongodb_client.MongoClient") as mock_client:
            mock_instance = Mock()
            mock_db = Mock()
            mock_collection = Mock()

            mock_client.return_value = mock_instance
            # Configure mock to return mock_db when accessing database
            mock_instance.__getitem__ = Mock(return_value=mock_db)
            # Configure mock_db to return mock_collection when accessing collection
            mock_db.__getitem__ = Mock(return_value=mock_collection)

            yield mock_client, mock_instance, mock_db, mock_collection

    @pytest.fixture
    def sample_story(self):
        """Sample story data for testing."""
        return {
            "headline": "Test Story",
            "summary": "This is a test story",
            "body": "Full story content here",
            "sources": ["https://example.com"],
        }

    def test_init_with_default_uri(self, mock_mongo_client):
        """Test initialization with default URI from config."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            client = MongoDBClient()

            mock_client.assert_called_once_with("mongodb://localhost:27017")
            assert client._client == mock_instance
            assert client._db == mock_db
            assert client._collection == mock_collection

    def test_init_with_custom_uri(self, mock_mongo_client):
        """Test initialization with custom URI."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        custom_uri = "mongodb://custom:27017"

        client = MongoDBClient(uri=custom_uri)

        mock_client.assert_called_once_with(custom_uri)
        assert client._client == mock_instance

    def test_init_with_none_uri_and_missing_config(self, mock_mongo_client):
        """Test initialization fails when URI is None and config is missing."""
        with (
            patch("clients.mongodb_client.MONGODB_URI", None),
            pytest.raises(ValueError, match="MONGODB_URI is missing"),
        ):
            MongoDBClient()

    def test_init_with_empty_uri_and_empty_config(self, mock_mongo_client):
        """Test initialization fails when URI is empty and config is empty."""
        with (
            patch("clients.mongodb_client.MONGODB_URI", ""),
            pytest.raises(ValueError, match="MONGODB_URI is missing"),
        ):
            MongoDBClient()

    def test_init_with_explicit_none_uri_and_missing_config(self, mock_mongo_client):
        """Test initialization fails when URI is explicitly None and config missing."""
        with (
            patch("clients.mongodb_client.MONGODB_URI", None),
            pytest.raises(ValueError, match="MONGODB_URI is missing"),
        ):
            MongoDBClient(uri=None)

    def test_insert_story_success(self, mock_mongo_client, sample_story):
        """Test successful story insertion."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        # Mock the insert_one result
        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result

        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            client = MongoDBClient()
            result = client.insert_story(sample_story)

            mock_collection.insert_one.assert_called_once_with(sample_story)
            assert result == str(mock_object_id)

    def test_insert_story_with_missing_headline(self, mock_mongo_client):
        """Test story insertion with missing headline (should still work)."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        story_without_headline = {
            "summary": "This is a test story",
            "body": "Full story content here",
        }

        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result

        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            client = MongoDBClient()
            result = client.insert_story(story_without_headline)

            mock_collection.insert_one.assert_called_once_with(story_without_headline)
            assert result == str(mock_object_id)

    def test_insert_story_empty_dict(self, mock_mongo_client):
        """Test insertion of empty story dictionary."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result

        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            client = MongoDBClient()
            result = client.insert_story({})

            mock_collection.insert_one.assert_called_once_with({})
            assert result == str(mock_object_id)

    @patch("clients.mongodb_client.logger")
    def test_logging_on_init(self, mock_logger, mock_mongo_client):
        """Test that initialization logs connection info."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_DATABASE_NAME", "test_db"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME", "test_collection"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME_AUDIO", "podcast"),
        ):
            MongoDBClient()

            # Should log both the main collection and the audio collection
            mock_logger.info.assert_any_call(
                "  ✓ MongoDB connected: %s/%s", "test_db", "test_collection"
            )
            mock_logger.info.assert_any_call(
                "  ✓ MongoDB audio collection ready: %s/%s", "test_db", "podcast"
            )

    @patch("clients.mongodb_client.logger")
    def test_logging_on_insert_story(self, mock_logger, mock_mongo_client, sample_story):
        """Test that insert_story logs the operation."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result

        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            client = MongoDBClient()
            client.insert_story(sample_story)

            # Debug logging was removed - no assertion needed
            pass

    def test_database_and_collection_configuration(self, mock_mongo_client):
        """Test that correct database and collection names are used."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_DATABASE_NAME", "breaking-news"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME", "stories"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME_AUDIO", "podcast"),
        ):
            MongoDBClient()

            # Verify database access
            mock_instance.__getitem__.assert_called_with("breaking-news")
            # Verify main collection access
            mock_db.__getitem__.assert_any_call("stories")
            # Verify audio collection access
            mock_db.__getitem__.assert_any_call("podcast")

    def test_init_missing_database_name(self, mock_mongo_client):
        """Test initialization fails when MONGODB_DATABASE_NAME is missing."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_DATABASE_NAME", ""),  # Empty string
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME", "stories"),
            pytest.raises(ValueError, match="MONGODB_DATABASE_NAME is missing"),
        ):
            MongoDBClient()

    def test_init_missing_collection_name(self, mock_mongo_client):
        """Test initialization fails when MONGODB_COLLECTION_NAME is missing."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_DATABASE_NAME", "breaking-news"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME", ""),  # Empty string
            pytest.raises(ValueError, match="MONGODB_COLLECTION_NAME is missing"),
        ):
            MongoDBClient()

    def test_init_none_database_name(self, mock_mongo_client):
        """Test initialization fails when MONGODB_DATABASE_NAME is None."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_DATABASE_NAME", None),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME", "stories"),
            pytest.raises(ValueError, match="MONGODB_DATABASE_NAME is missing"),
        ):
            MongoDBClient()

    def test_init_none_collection_name(self, mock_mongo_client):
        """Test initialization fails when MONGODB_COLLECTION_NAME is None."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_DATABASE_NAME", "breaking-news"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME", None),
            pytest.raises(ValueError, match="MONGODB_COLLECTION_NAME is missing"),
        ):
            MongoDBClient()

    def test_context_manager(self, mock_mongo_client):
        """Test context manager functionality."""
        mock_client, mock_instance, _, _ = mock_mongo_client

        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            # Use client as a context manager
            with MongoDBClient() as client:
                assert client._client == mock_instance

            # Verify close was called on exit
            mock_instance.close.assert_called_once()

    def test_close_method(self, mock_mongo_client):
        """Test explicit close method."""
        mock_client, mock_instance, _, _ = mock_mongo_client

        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            client = MongoDBClient()
            client.close()

            # Verify close was called
            mock_instance.close.assert_called_once()

    def test_insert_podcast(self, mock_mongo_client):
        """Test inserting podcast data."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        # Set up audio collection
        mock_audio_collection = Mock()
        mock_db.__getitem__.side_effect = (
            lambda x: mock_audio_collection if x == "audio" else mock_collection
        )

        # Mock the insert_one result
        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_audio_collection.insert_one.return_value = mock_result

        podcast_data = {
            "title": "Test Podcast",
            "description": "Test Description",
            "audio_url": "https://example.com/test.mp3",
        }

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME_AUDIO", "audio"),
        ):
            client = MongoDBClient()
            result = client.insert_podcast(podcast_data)

            mock_audio_collection.insert_one.assert_called_once_with(podcast_data)
            assert result == str(mock_object_id)

    def test_insert_podcast_no_audio_collection(self, mock_mongo_client):
        """Test inserting podcast without audio collection configured."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        podcast_data = {"title": "Test Podcast"}

        with (
            patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"),
            patch("clients.mongodb_client.MONGODB_COLLECTION_NAME_AUDIO", None),
        ):
            client = MongoDBClient()

            with pytest.raises(ValueError, match="Audio collection not configured"):
                client.insert_podcast(podcast_data)

    def test_get_recent_stories(self, mock_mongo_client):
        """Test retrieving recent stories."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client

        # Sample return value from find
        mock_stories = [{"summary": "Story 1"}, {"summary": "Story 2"}]
        mock_collection.find.return_value = mock_stories

        # Setup the client
        with patch("clients.mongodb_client.MONGODB_URI", "mongodb://localhost:27017"):
            client = MongoDBClient()
            result = client.get_recent_stories(hours=24)

            # Verify find was called with correct query
            mock_collection.find.assert_called_once()
            query_arg = mock_collection.find.call_args[0][0]
            assert "_id" in query_arg
            assert "$gte" in query_arg["_id"]

            # Verify result
            assert result == mock_stories
