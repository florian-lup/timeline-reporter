"""Test suite for storage service."""

from unittest.mock import Mock, patch

import pytest

from services import insert_articles
from models import Article


class TestStorageService:
    """Test suite for storage service functions."""

    @pytest.fixture
    def mock_mongodb_client(self):
        """Mock MongoDB client for testing."""
        return Mock()

    @pytest.fixture
    def sample_articles(self):
        """Sample articles for testing."""
        return [
            Article(
                headline="Climate Summit Agreement",
                summary="World leaders reach consensus on climate action.",
                story="Detailed story about the climate summit and its outcomes.",
                sources=["https://example.com/climate"],
            ),
            Article(
                headline="Tech Innovation News",
                summary="Breakthrough in AI technology announced.",
                story="Comprehensive coverage of the latest AI developments.",
                sources=["https://example.com/tech"],
            ),
        ]

    def test_insert_articles_success(self, mock_mongodb_client, sample_articles):
        """Test successful article storage."""
        mock_mongodb_client.insert_article.side_effect = [
            "60a1b2c3d4e5f6789",
            "60a1b2c3d4e5f6790",
        ]

        with patch("services.article_insertion.logger") as mock_logger:
            insert_articles(sample_articles, mongodb_client=mock_mongodb_client)

        # Verify MongoDB calls
        assert mock_mongodb_client.insert_article.call_count == 2

        # Verify article dictionaries were passed correctly
        call_args = mock_mongodb_client.insert_article.call_args_list

        # First article
        first_article_dict = call_args[0][0][0]
        assert first_article_dict["headline"] == "Climate Summit Agreement"
        assert first_article_dict["summary"] == "World leaders reach consensus on climate action."
        assert first_article_dict["story"] == "Detailed story about the climate summit and its outcomes."

        # Second article
        second_article_dict = call_args[1][0][0]
        assert second_article_dict["headline"] == "Tech Innovation News"
        assert second_article_dict["summary"] == "Breakthrough in AI technology announced."
        assert second_article_dict["story"] == "Comprehensive coverage of the latest AI developments."

        # Verify logging
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call(
            "Stored article: '%s' (id=%s)",
            "Climate Summit Agreement",
            "60a1b2c3d4e5f6789",
        )
        mock_logger.info.assert_any_call(
            "Stored article: '%s' (id=%s)", "Tech Innovation News", "60a1b2c3d4e5f6790"
        )

    def test_insert_articles_empty_list(self, mock_mongodb_client):
        """Test storage with empty article list."""
        with patch("services.article_insertion.logger") as mock_logger:
            insert_articles([], mongodb_client=mock_mongodb_client)

        mock_mongodb_client.insert_article.assert_not_called()
        mock_logger.info.assert_not_called()

    def test_insert_articles_single_article(self, mock_mongodb_client):
        """Test storage with single article."""
        single_article = [
            Article(
                headline="Single Article",
                summary="Single article summary",
                story="Single article story",
                sources=["https://example.com"],
            )
        ]

        mock_mongodb_client.insert_article.return_value = "60a1b2c3d4e5f6789"

        insert_articles(single_article, mongodb_client=mock_mongodb_client)

        mock_mongodb_client.insert_article.assert_called_once()
        call_args = mock_mongodb_client.insert_article.call_args[0][0]
        assert call_args["headline"] == "Single Article"

    def test_insert_articles_article_dict_conversion(
        self, mock_mongodb_client, sample_articles
    ):
        """Test that articles are properly converted to dictionaries."""
        mock_mongodb_client.insert_article.side_effect = ["id1", "id2"]

        insert_articles(sample_articles, mongodb_client=mock_mongodb_client)

        # Verify article conversion
        call_args = mock_mongodb_client.insert_article.call_args_list
        for i, call in enumerate(call_args):
            article_dict = call[0][0]
            original_article = sample_articles[i]

            # Verify all fields are present
            assert article_dict["headline"] == original_article.headline
            assert article_dict["summary"] == original_article.summary
            assert article_dict["story"] == original_article.story
            assert article_dict["sources"] == original_article.sources

    def test_insert_articles_mongodb_error_handling(
        self, mock_mongodb_client, sample_articles
    ):
        """Test error handling when MongoDB insertion fails."""
        mock_mongodb_client.insert_article.side_effect = Exception("Database error")

        # Should propagate the exception
        with pytest.raises(Exception, match="Database error"):
            insert_articles(sample_articles, mongodb_client=mock_mongodb_client)

    def test_insert_articles_with_unicode_content(self, mock_mongodb_client):
        """Test storage with unicode characters."""
        unicode_article = [
            Article(
                headline="Climate Summit 🌍 Results",
                summary="Leaders discuss émissions reduction",
                story="The summit in København addressed climate change",
                sources=["https://example.com/climate-🌍"],
            )
        ]

        mock_mongodb_client.insert_article.return_value = "unicode_id"

        insert_articles(unicode_article, mongodb_client=mock_mongodb_client)

        call_args = mock_mongodb_client.insert_article.call_args[0][0]
        assert "🌍" in call_args["headline"]
        assert "émissions" in call_args["summary"]
        assert "København" in call_args["story"]

    def test_insert_articles_large_batch(self, mock_mongodb_client):
        """Test storage with large number of articles."""
        large_batch = [
            Article(
                headline=f"Article {i}",
                summary=f"Summary {i}",
                story=f"Story {i}",
                sources=[f"https://example.com/{i}"],
            )
            for i in range(100)
        ]

        mock_mongodb_client.insert_article.side_effect = [
            f"id{i}" for i in range(100)
        ]

        insert_articles(large_batch, mongodb_client=mock_mongodb_client)

        # Verify all articles were processed
        assert mock_mongodb_client.insert_article.call_count == 100

        # Verify data integrity for first and last articles
        first_call = mock_mongodb_client.insert_article.call_args_list[0][0][0]
        last_call = mock_mongodb_client.insert_article.call_args_list[-1][0][0]

        assert first_call["headline"] == "Article 0"
        assert last_call["headline"] == "Article 99"
