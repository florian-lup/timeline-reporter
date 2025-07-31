"""Test suite for story persistence service."""

from unittest.mock import Mock, patch

import pytest

from models import Story, Podcast
from services import persist_stories, persist_podcast, persist_stories_and_podcast


class TestPersistenceService:
    """Test suite for story persistence service functions."""

    @pytest.fixture
    def mock_mongodb_client(self):
        """Mock MongoDB client for testing."""
        return Mock()

    @pytest.fixture
    def sample_stories(self):
        """Sample stories for testing."""
        return [
            Story(
                headline="Climate Summit Agreement",
                summary="World leaders reach consensus on climate action.",
                body="Detailed story about the climate summit and its outcomes.",
                tag="environment",
                sources=["https://example.com/climate-news"],
            ),
            Story(
                headline="Tech Innovation News",
                summary="Breakthrough in AI technology announced.",
                body="Comprehensive coverage of the latest AI developments.",
                tag="technology",
                sources=["https://example.com/tech-news"],
            ),
        ]

    def test_persist_stories_success(self, mock_mongodb_client, sample_stories):
        """Test successful story storage."""
        mock_mongodb_client.insert_story.side_effect = [
            "60a1b2c3d4e5f6789",
            "60a1b2c3d4e5f6790",
        ]

        # No return value expected
        persist_stories(sample_stories, mongodb_client=mock_mongodb_client)

        # Verify storage calls
        assert mock_mongodb_client.insert_story.call_count == 2

        # Verify story dictionaries were passed correctly
        call_args = mock_mongodb_client.insert_story.call_args_list

        # First story
        first_story_dict = call_args[0][0][0]
        assert first_story_dict["headline"] == "Climate Summit Agreement"
        assert first_story_dict["summary"] == "World leaders reach consensus on climate action."
        assert first_story_dict["body"] == "Detailed story about the climate summit and its outcomes."

        # Second story
        second_story_dict = call_args[1][0][0]
        assert second_story_dict["headline"] == "Tech Innovation News"
        assert second_story_dict["summary"] == "Breakthrough in AI technology announced."
        assert second_story_dict["body"] == "Comprehensive coverage of the latest AI developments."

    @patch("services.story_persistence.logger")
    def test_persist_stories_logging(self, mock_logger, mock_mongodb_client, sample_stories):
        """Test that storage logging works correctly."""
        mock_mongodb_client.insert_story.side_effect = [
            "60a1b2c3d4e5f6789",
            "60a1b2c3d4e5f6790",
        ]

        persist_stories(sample_stories, mongodb_client=mock_mongodb_client)

        # Verify individual story logging - updated to match new emoji-based format
        # Check the exact logging calls (first 5 words of headline + "...")
        mock_logger.info.assert_any_call(
            "  ✓ Story %d/%d saved successfully - %s (ID: %s)",
            1,
            2,
            "Climate Summit Agreement...",
            "60a1b2c3d4e5...",
        )
        mock_logger.info.assert_any_call(
            "  ✓ Story %d/%d saved successfully - %s (ID: %s)",
            2,
            2,
            "Tech Innovation News...",
            "60a1b2c3d4e5...",
        )

    def test_persist_stories_empty_list(self, mock_mongodb_client):
        """Test storage with empty story list."""

        persist_stories([], mongodb_client=mock_mongodb_client)

        mock_mongodb_client.insert_story.assert_not_called()

    def test_persist_stories_single_story(self, mock_mongodb_client):
        """Test storage with single story."""
        single_story = [
            Story(
                headline="Single Story",
                summary="Single story summary",
                body="Single story content",
                tag="other",
                sources=["https://example.com/single"],
            )
        ]

        mock_mongodb_client.insert_story.return_value = "60a1b2c3d4e5f6789"

        persist_stories(single_story, mongodb_client=mock_mongodb_client)

        assert mock_mongodb_client.insert_story.call_count == 1

    def test_persist_stories_story_dict_conversion(self, mock_mongodb_client, sample_stories):
        """Test that stories are properly converted to dictionaries."""
        mock_mongodb_client.insert_story.side_effect = ["id1", "id2"]

        persist_stories(sample_stories, mongodb_client=mock_mongodb_client)

        # Verify dictionary conversion for each story
        call_args_list = mock_mongodb_client.insert_story.call_args_list

        for i, call in enumerate(call_args_list):
            story_dict = call[0][0]
            original_story = sample_stories[i]

            assert story_dict["headline"] == original_story.headline
            assert story_dict["summary"] == original_story.summary
            assert story_dict["body"] == original_story.body
            assert story_dict["sources"] == original_story.sources

    def test_persist_stories_mongodb_error_handling(self, mock_mongodb_client, sample_stories):
        """Test error handling for MongoDB insertion failures."""
        mock_mongodb_client.insert_story.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            persist_stories(sample_stories, mongodb_client=mock_mongodb_client)

    def test_persist_stories_with_unicode_content(self, mock_mongodb_client):
        """Test storage with unicode characters in content."""
        unicode_story = [
            Story(
                headline="Événement Important 🌍",
                summary="Résumé avec caractères spéciaux: àáäâ",
                body="Contenu détaillé avec émojis 🚀 et accents",
                tag="international",
                sources=["https://example.com/unicode"],
            )
        ]

        mock_mongodb_client.insert_story.return_value = "60a1b2c3d4e5f6789"

        persist_stories(unicode_story, mongodb_client=mock_mongodb_client)

        # Verify unicode content is preserved
        story_dict = mock_mongodb_client.insert_story.call_args[0][0]
        assert "🌍" in story_dict["headline"]
        assert "àáäâ" in story_dict["summary"]

    def test_persist_stories_large_batch(self, mock_mongodb_client):
        """Test storage with large number of stories."""
        large_batch = [
            Story(
                headline=f"Story {i}",
                summary=f"Summary {i}",
                body=f"Body {i}",
                tag="other",
                sources=[f"https://example.com/{i}"],
            )
            for i in range(100)
        ]

        mock_mongodb_client.insert_story.return_value = "60a1b2c3d4e5f6789"

        persist_stories(large_batch, mongodb_client=mock_mongodb_client)

        # Verify all stories were processed
        assert mock_mongodb_client.insert_story.call_count == 100

        # Verify data integrity for first and last stories
        first_call = mock_mongodb_client.insert_story.call_args_list[0][0][0]
        last_call = mock_mongodb_client.insert_story.call_args_list[-1][0][0]

        assert first_call["headline"] == "Story 0"
        assert last_call["headline"] == "Story 99"

    @pytest.fixture
    def sample_podcast(self):
        """Sample podcast for testing."""
        return Podcast(
            anchor_script="Welcome to the daily news update. Today's top stories are...",
            anchor_name="News Anchor",
            audio_url="https://cdn.example.com/podcasts/12345.mp3",
            audio_size_bytes=1024000
        )

    @patch("services.story_persistence.logger")
    def test_persist_podcast(self, mock_logger, mock_mongodb_client, sample_podcast):
        """Test podcast persistence function."""
        mock_mongodb_client.insert_podcast.return_value = "60a1b2c3d4e5f6789"
        
        result = persist_podcast(sample_podcast, mongodb_client=mock_mongodb_client)
        
        # Verify the correct ID was returned
        assert result == "60a1b2c3d4e5f6789"
        
        # Verify MongoDB client was called with podcast dict
        mock_mongodb_client.insert_podcast.assert_called_once()
        podcast_dict = mock_mongodb_client.insert_podcast.call_args[0][0]
        assert podcast_dict["anchor_script"] == "Welcome to the daily news update. Today's top stories are..."
        assert podcast_dict["anchor_name"] == "News Anchor"
        assert podcast_dict["audio_url"] == "https://cdn.example.com/podcasts/12345.mp3"
        
        # Verify logging
        mock_logger.info.assert_any_call("🎙️ STEP 7: Persistence - Saving podcast metadata to database...")
        mock_logger.info.assert_any_call("  💾 Saving podcast metadata...")
        mock_logger.info.assert_any_call("  ✓ Podcast saved with CDN URL (ID: %s)", "60a1b2c3d4e5...")
        mock_logger.info.assert_any_call("✅ Persistence complete: podcast metadata stored")

    @patch("services.story_persistence.logger")
    def test_persist_stories_and_podcast(self, mock_logger, mock_mongodb_client, sample_stories, sample_podcast):
        """Test combined persistence of stories and podcast."""
        mock_mongodb_client.insert_story.side_effect = ["id1", "id2"]
        mock_mongodb_client.insert_podcast.return_value = "60a1b2c3d4e5f6789"
        
        result = persist_stories_and_podcast(
            sample_stories, sample_podcast, mongodb_client=mock_mongodb_client
        )
        
        # Verify the correct ID was returned
        assert result == "60a1b2c3d4e5f6789"
        
        # Verify stories were persisted
        assert mock_mongodb_client.insert_story.call_count == 2
        
        # Verify podcast was persisted
        mock_mongodb_client.insert_podcast.assert_called_once()
        podcast_dict = mock_mongodb_client.insert_podcast.call_args[0][0]
        assert podcast_dict["anchor_name"] == "News Anchor"
        
        # Verify logging
        mock_logger.info.assert_any_call("🎙️ STEP 7: Persistence - Saving stories and podcast metadata...")
        mock_logger.info.assert_any_call("  📰 Persisting %d stories...", 2)
        mock_logger.info.assert_any_call("  🎙️ Persisting podcast metadata...")
        mock_logger.info.assert_any_call("  ✓ Podcast saved with CDN URL (ID: %s)", "60a1b2c3d4e5...")
        mock_logger.info.assert_any_call("✅ Persistence complete: %d stories and podcast saved", 2)
