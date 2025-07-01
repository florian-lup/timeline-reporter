"""Test suite for storage service."""

import pytest
from unittest.mock import Mock, patch

from services import store_articles
from utils import Article


class TestStorageService:
    """Test suite for storage service functions."""

    @pytest.fixture
    def mock_mongodb_client(self):
        """Mock MongoDB client for testing."""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def sample_articles(self):
        """Sample articles for testing."""
        return [
            Article(
                headline="Climate Summit Agreement",
                summary="World leaders reach consensus on climate action.",
                story="Detailed story about the climate summit and its outcomes.",
                sources=["https://example.com/climate"],
                broadcast=b"audio_data_1",
                reporter="Alex"
            ),
            Article(
                headline="Tech Innovation News",
                summary="Breakthrough in AI technology announced.",
                story="Comprehensive coverage of the latest AI developments.",
                sources=["https://example.com/tech"],
                broadcast=b"audio_data_2",
                reporter="Blake"
            )
        ]

    def test_store_articles_success(self, mock_mongodb_client, sample_articles):
        """Test successful article storage."""
        mock_mongodb_client.insert_article.side_effect = ["60a1b2c3d4e5f6789", "60a1b2c3d4e5f6790"]
        
        with patch('services.storage.logger') as mock_logger:
            store_articles(sample_articles, mongodb_client=mock_mongodb_client)
        
        # Verify MongoDB calls
        assert mock_mongodb_client.insert_article.call_count == 2
        
        # Verify article dictionaries were passed correctly
        call_args = mock_mongodb_client.insert_article.call_args_list
        
        # First article
        first_article_dict = call_args[0][0][0]
        assert first_article_dict['headline'] == "Climate Summit Agreement"
        assert first_article_dict['broadcast'] == b"audio_data_1"
        assert first_article_dict['reporter'] == "Alex"
        
        # Second article
        second_article_dict = call_args[1][0][0]
        assert second_article_dict['headline'] == "Tech Innovation News"
        assert second_article_dict['broadcast'] == b"audio_data_2"
        assert second_article_dict['reporter'] == "Blake"
        
        # Verify logging
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call(
            "Stored article '%s' (id=%s)", 
            "Climate Summit Agreement", 
            "60a1b2c3d4e5f6789"
        )
        mock_logger.info.assert_any_call(
            "Stored article '%s' (id=%s)", 
            "Tech Innovation News", 
            "60a1b2c3d4e5f6790"
        )

    def test_store_articles_empty_list(self, mock_mongodb_client):
        """Test storage with empty article list."""
        with patch('services.storage.logger') as mock_logger:
            store_articles([], mongodb_client=mock_mongodb_client)
        
        mock_mongodb_client.insert_article.assert_not_called()
        mock_logger.info.assert_not_called()

    def test_store_articles_single_article(self, mock_mongodb_client):
        """Test storage with single article."""
        single_article = [
            Article(
                headline="Single Article",
                summary="Single article summary",
                story="Single article story",
                sources=["https://example.com"],
                broadcast=b"single_audio",
                reporter="Reporter"
            )
        ]
        
        mock_mongodb_client.insert_article.return_value = "60a1b2c3d4e5f6789"
        
        store_articles(single_article, mongodb_client=mock_mongodb_client)
        
        mock_mongodb_client.insert_article.assert_called_once()
        call_args = mock_mongodb_client.insert_article.call_args[0][0]
        assert call_args['headline'] == "Single Article"

    def test_store_articles_article_dict_conversion(self, mock_mongodb_client, sample_articles):
        """Test that articles are properly converted to dictionaries."""
        mock_mongodb_client.insert_article.side_effect = ["id1", "id2"]
        
        store_articles(sample_articles, mongodb_client=mock_mongodb_client)
        
        # Verify article conversion
        call_args = mock_mongodb_client.insert_article.call_args_list
        for i, call in enumerate(call_args):
            article_dict = call[0][0]
            original_article = sample_articles[i]
            
            # Verify all fields are present
            assert article_dict['headline'] == original_article.headline
            assert article_dict['summary'] == original_article.summary
            assert article_dict['story'] == original_article.story
            assert article_dict['sources'] == original_article.sources
            assert article_dict['broadcast'] == original_article.broadcast
            assert article_dict['reporter'] == original_article.reporter

    def test_store_articles_mongodb_error_handling(self, mock_mongodb_client, sample_articles):
        """Test error handling when MongoDB insertion fails."""
        mock_mongodb_client.insert_article.side_effect = Exception("Database error")
        
        # Should propagate the exception
        with pytest.raises(Exception, match="Database error"):
            store_articles(sample_articles, mongodb_client=mock_mongodb_client)

    def test_store_articles_with_unicode_content(self, mock_mongodb_client):
        """Test storage with unicode characters."""
        unicode_article = [
            Article(
                headline="Climate Summit 🌍 Results",
                summary="Leaders discuss émissions reduction",
                story="The summit in København addressed climate change",
                sources=["https://example.com/climate-🌍"],
                broadcast=b"unicode_audio_data",
                reporter="François"
            )
        ]
        
        mock_mongodb_client.insert_article.return_value = "unicode_id"
        
        store_articles(unicode_article, mongodb_client=mock_mongodb_client)
        
        call_args = mock_mongodb_client.insert_article.call_args[0][0]
        assert "🌍" in call_args['headline']
        assert "émissions" in call_args['summary']
        assert "København" in call_args['story']
        assert "François" == call_args['reporter']

    @pytest.mark.parametrize("article_count", [1, 5, 10, 50])
    def test_store_articles_various_counts(self, mock_mongodb_client, article_count):
        """Test storage with various article counts."""
        articles = []
        expected_ids = []
        
        for i in range(article_count):
            articles.append(
                Article(
                    headline=f"Article {i}",
                    summary=f"Summary {i}",
                    story=f"Story {i}",
                    sources=[f"https://example.com/{i}"],
                    broadcast=f"audio_{i}".encode(),
                    reporter=f"Reporter{i}"
                )
            )
            expected_ids.append(f"id_{i}")
        
        mock_mongodb_client.insert_article.side_effect = expected_ids
        
        store_articles(articles, mongodb_client=mock_mongodb_client)
        
        assert mock_mongodb_client.insert_article.call_count == article_count 