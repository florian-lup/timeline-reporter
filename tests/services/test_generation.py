"""Test suite for audio generation service."""

import json
from unittest.mock import Mock, patch

import pytest

from models import Podcast, Story
from services.audio_generation import generate_podcast


class TestAudioGeneration:
    """Test suite for audio generation service functions."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        mock_client = Mock()
        mock_client.chat_completion.return_value = "Good morning, this is your daily news briefing for January 15th, 2024..."
        mock_client.text_to_speech.return_value = b"fake_audio_bytes_content"
        return mock_client

    @pytest.fixture
    def mock_mongodb_client(self):
        """Mock MongoDB client for testing."""
        mock_client = Mock()
        mock_client.insert_podcast.return_value = "64a7b8c9d1e2f3a4b5c6d7e8"
        return mock_client

    @pytest.fixture
    def sample_stories(self):
        """Sample stories for testing."""
        return [
            Story(
                headline="Climate Summit 2024 Concludes with Historic Agreement",
                summary="World leaders reached unprecedented consensus on carbon reduction targets",
                body="The Climate Summit 2024 concluded today with historic agreements...",
                tag="environment",
                sources=["https://example.com/climate-news"],
                date="2024-01-15",
            ),
            Story(
                headline="AI Breakthrough in Medical Diagnosis",
                summary="New AI system demonstrates 95% accuracy in early cancer detection",
                body="Researchers at major medical institutions have developed...",
                tag="technology",
                sources=["https://example.com/medical-ai"],
                date="2024-01-15",
            ),
        ]

    @pytest.fixture
    def single_story(self):
        """Single story for testing."""
        return [
            Story(
                headline="Technology Innovation Announcement",
                summary="Major tech company announces breakthrough in quantum computing",
                body="In a groundbreaking announcement today...",
                tag="technology",
                sources=["https://example.com/quantum-tech"],
                date="2024-01-15",
            )
        ]

    def test_generate_podcast_success(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test successful podcast generation with multiple stories."""
        podcast = generate_podcast(
            sample_stories,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        assert isinstance(podcast, Podcast)
        assert len(podcast.anchor_script) > 0
        assert len(podcast.audio_file) > 0
        assert podcast.audio_file == b"fake_audio_bytes_content"

        # Verify OpenAI client was called for script generation
        mock_openai_client.chat_completion.assert_called_once()
        # Verify OpenAI client was called for TTS
        mock_openai_client.text_to_speech.assert_called_once()
        # Verify MongoDB insertion
        mock_mongodb_client.insert_podcast.assert_called_once()

    def test_generate_podcast_single_story(self, mock_openai_client, mock_mongodb_client, single_story):
        """Test podcast generation with single story."""
        podcast = generate_podcast(
            single_story,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        assert isinstance(podcast, Podcast)
        assert len(podcast.anchor_script) > 0
        assert len(podcast.audio_file) > 0

    def test_generate_podcast_empty_stories_list(self, mock_openai_client, mock_mongodb_client):
        """Test podcast generation with empty stories list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot generate podcast without stories"):
            generate_podcast(
                [],
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )

        # Verify no API calls were made
        mock_openai_client.chat_completion.assert_not_called()
        mock_openai_client.text_to_speech.assert_not_called()
        mock_mongodb_client.insert_podcast.assert_not_called()

    def test_generate_podcast_anchor_script_parameters(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that anchor script generation uses correct parameters."""
        generate_podcast(
            sample_stories,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        # Verify chat completion was called with correct model
        call_args = mock_openai_client.chat_completion.call_args
        assert call_args[1]["model"] == "gpt-4.1-mini-2025-04-14"

    def test_generate_podcast_tts_parameters(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that text-to-speech uses correct parameters."""
        from config.audio_config import TTS_MODEL, TTS_SPEED, AUDIO_FORMAT, VOICE_ANCHOR_MAPPING
        
        anchor_script = "Test anchor script content"
        mock_openai_client.chat_completion.return_value = anchor_script

        generate_podcast(
            sample_stories,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        # Verify TTS was called with correct parameters
        call_args = mock_openai_client.text_to_speech.call_args
        assert call_args[0][0] == anchor_script  # First arg is the script text
        assert call_args[1]["model"] == TTS_MODEL
        assert call_args[1]["voice"] in VOICE_ANCHOR_MAPPING  # Voice should be one of the configured voices
        assert call_args[1]["speed"] == TTS_SPEED
        assert call_args[1]["response_format"] == AUDIO_FORMAT

    def test_generate_podcast_prompt_formatting(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that prompts are formatted correctly with story summaries."""
        generate_podcast(
            sample_stories,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        # Verify prompt contains expected elements
        call_args = mock_openai_client.chat_completion.call_args
        prompt = call_args[0][0]  # First positional argument is the prompt

        # Should contain story summaries
        assert "Story 1:" in prompt
        assert "Story 2:" in prompt
        assert sample_stories[0].summary in prompt
        assert sample_stories[1].summary in prompt

        # Should contain system prompt elements
        assert "professional news anchor" in prompt.lower()
        assert "news briefing podcast" in prompt.lower()

        # Prompt should not include explicit story count now

    def test_generate_podcast_mongodb_insertion(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that podcast is properly inserted into MongoDB."""
        generate_podcast(
            sample_stories,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        # Verify MongoDB insertion was called
        mock_mongodb_client.insert_podcast.assert_called_once()
        
        # Verify the inserted data structure
        call_args = mock_mongodb_client.insert_podcast.call_args
        inserted_data = call_args[0][0]
        
        assert "anchor_script" in inserted_data
        assert "audio_file" in inserted_data

    @patch("services.audio_generation.logger")
    def test_generate_podcast_logging(self, mock_logger, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that podcast generation logs appropriately."""
        generate_podcast(
            sample_stories,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        # Verify key log messages were called
        mock_logger.info.assert_any_call("🎙️ STEP 7: Audio Generation - Creating news briefing podcast...")
        mock_logger.info.assert_any_call("  📝 Extracting summaries from %d stories...", 2)
        mock_logger.info.assert_any_call("  🎬 Generating anchor script with %s...", "gpt-4.1-mini-2025-04-14")

    @patch("services.audio_generation.logger")
    def test_generate_podcast_empty_stories_logging(self, mock_logger, mock_openai_client, mock_mongodb_client):
        """Test that empty stories list logs warning."""
        with pytest.raises(ValueError):
            generate_podcast(
                [],
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )

        mock_logger.warning.assert_called_once_with("No stories provided for podcast generation")

    def test_generate_podcast_openai_script_error(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test handling of OpenAI script generation errors."""
        mock_openai_client.chat_completion.side_effect = Exception("OpenAI API Error")

        with pytest.raises(Exception, match="OpenAI API Error"):
            generate_podcast(
                sample_stories,
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )

        # Verify TTS was not called due to script generation failure
        mock_openai_client.text_to_speech.assert_not_called()
        mock_mongodb_client.insert_podcast.assert_not_called()

    def test_generate_podcast_tts_error(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test handling of TTS generation errors."""
        mock_openai_client.text_to_speech.side_effect = Exception("TTS API Error")

        with pytest.raises(Exception, match="TTS API Error"):
            generate_podcast(
                sample_stories,
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )

        # Verify script generation was called but podcast was not saved
        mock_openai_client.chat_completion.assert_called_once()
        mock_mongodb_client.insert_podcast.assert_not_called()

    def test_generate_podcast_mongodb_error(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test handling of MongoDB insertion errors."""
        mock_mongodb_client.insert_podcast.side_effect = Exception("MongoDB Error")

        with pytest.raises(Exception, match="MongoDB Error"):
            generate_podcast(
                sample_stories,
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )

        # Verify both OpenAI calls were made before MongoDB error
        mock_openai_client.chat_completion.assert_called_once()
        mock_openai_client.text_to_speech.assert_called_once()

    def test_generate_podcast_audio_file_size_logging(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that audio file size is logged correctly."""
        large_audio_data = b"x" * (1024 * 1024)  # 1 MB of data
        mock_openai_client.text_to_speech.return_value = large_audio_data

        with patch("services.audio_generation.logger") as mock_logger:
            podcast = generate_podcast(
                sample_stories,
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )

            # Verify audio size logging
            mock_logger.info.assert_any_call("  ✓ Audio generated: %.1f MB", 1.0)

        assert len(podcast.audio_file) == 1024 * 1024

    def test_generate_podcast_script_word_count_logging(self, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that script word count is logged correctly."""
        test_script = "This is a test script with exactly ten words total"
        mock_openai_client.chat_completion.return_value = test_script

        with patch("services.audio_generation.logger") as mock_logger:
            generate_podcast(
                sample_stories,
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )

            # Verify word count logging
            mock_logger.info.assert_any_call("  ✓ Anchor script generated: %d words", 10)

    @patch("services.audio_generation.get_today_formatted")
    def test_generate_podcast_date_formatting(self, mock_date, mock_openai_client, mock_mongodb_client, sample_stories):
        """Test that date is properly formatted in the prompt."""
        mock_date.return_value = "January 15th, 2024"

        generate_podcast(
            sample_stories,
            openai_client=mock_openai_client,
            mongodb_client=mock_mongodb_client
        )

        # Verify the date was used in the prompt
        call_args = mock_openai_client.chat_completion.call_args
        prompt = call_args[0][0]
        assert "January 15th, 2024" in prompt
