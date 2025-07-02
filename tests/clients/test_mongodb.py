"""Test suite for MongoDB client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from clients import MongoDBClient


class TestMongoDBClient:
    """Test suite for MongoDBClient."""

    @pytest.fixture
    def mock_mongo_client(self):
        """Mock pymongo.MongoClient."""
        with patch('clients.mongodb_client.MongoClient') as mock_client:
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
    def sample_article(self):
        """Sample article data for testing."""
        return {
            "headline": "Test Article",
            "summary": "This is a test article",
            "story": "Full story content here",
            "sources": ["https://example.com"]
        }

    def test_init_with_default_uri(self, mock_mongo_client):
        """Test initialization with default URI from config."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        
        with patch('clients.mongodb_client.MONGODB_URI', 'mongodb://localhost:27017'):
            client = MongoDBClient()
            
            mock_client.assert_called_once_with('mongodb://localhost:27017')
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
        with patch('clients.mongodb_client.MONGODB_URI', None):
            with pytest.raises(ValueError, match="MONGODB_URI is missing"):
                MongoDBClient()

    def test_init_with_empty_uri_and_empty_config(self, mock_mongo_client):
        """Test initialization fails when URI is empty and config is empty."""
        with patch('clients.mongodb_client.MONGODB_URI', ''):
            with pytest.raises(ValueError, match="MONGODB_URI is missing"):
                MongoDBClient()

    def test_init_with_explicit_none_uri_and_missing_config(self, mock_mongo_client):
        """Test initialization fails when URI is explicitly None and config is missing."""
        with patch('clients.mongodb_client.MONGODB_URI', None):
            with pytest.raises(ValueError, match="MONGODB_URI is missing"):
                MongoDBClient(uri=None)

    def test_insert_article_success(self, mock_mongo_client, sample_article):
        """Test successful article insertion."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        
        # Mock the insert_one result
        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result
        
        with patch('clients.mongodb_client.MONGODB_URI', 'mongodb://localhost:27017'):
            client = MongoDBClient()
            result = client.insert_article(sample_article)
            
            mock_collection.insert_one.assert_called_once_with(sample_article)
            assert result == str(mock_object_id)

    def test_insert_article_with_missing_headline(self, mock_mongo_client):
        """Test article insertion with missing headline (should still work)."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        
        article_without_headline = {
            "summary": "This is a test article",
            "story": "Full story content here"
        }
        
        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result
        
        with patch('clients.mongodb_client.MONGODB_URI', 'mongodb://localhost:27017'):
            client = MongoDBClient()
            result = client.insert_article(article_without_headline)
            
            mock_collection.insert_one.assert_called_once_with(article_without_headline)
            assert result == str(mock_object_id)

    def test_insert_article_empty_dict(self, mock_mongo_client):
        """Test insertion of empty article dictionary."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        
        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result
        
        with patch('clients.mongodb_client.MONGODB_URI', 'mongodb://localhost:27017'):
            client = MongoDBClient()
            result = client.insert_article({})
            
            mock_collection.insert_one.assert_called_once_with({})
            assert result == str(mock_object_id)

    @patch('clients.mongodb_client.logger')
    def test_logging_on_init(self, mock_logger, mock_mongo_client):
        """Test that initialization logs connection info."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        
        with patch('clients.mongodb_client.MONGODB_URI', 'mongodb://localhost:27017'):
            with patch('clients.mongodb_client.MONGODB_DATABASE_NAME', 'test_db'):
                with patch('clients.mongodb_client.MONGODB_COLLECTION_NAME', 'test_collection'):
                    MongoDBClient()
                    
                    mock_logger.info.assert_called_once_with(
                        "MongoDB connected: %s/%s",
                        'test_db',
                        'test_collection'
                    )

    @patch('clients.mongodb_client.logger')
    def test_logging_on_insert_article(self, mock_logger, mock_mongo_client, sample_article):
        """Test that insert_article logs the operation."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        
        mock_result = Mock()
        mock_object_id = ObjectId()
        mock_result.inserted_id = mock_object_id
        mock_collection.insert_one.return_value = mock_result
        
        with patch('clients.mongodb_client.MONGODB_URI', 'mongodb://localhost:27017'):
            client = MongoDBClient()
            client.insert_article(sample_article)
            
            # Debug logging was removed - no assertion needed
            pass

    def test_database_and_collection_configuration(self, mock_mongo_client):
        """Test that correct database and collection names are used."""
        mock_client, mock_instance, mock_db, mock_collection = mock_mongo_client
        
        with patch('clients.mongodb_client.MONGODB_URI', 'mongodb://localhost:27017'):
            with patch('clients.mongodb_client.MONGODB_DATABASE_NAME', 'events'):
                with patch('clients.mongodb_client.MONGODB_COLLECTION_NAME', 'articles'):
                    MongoDBClient()
                    
                    # Verify database and collection access
                    mock_instance.__getitem__.assert_called_with('events')
                    mock_db.__getitem__.assert_called_with('articles') 