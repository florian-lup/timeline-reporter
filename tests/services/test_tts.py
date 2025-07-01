"""Test suite for TTS service."""

import pytest
from unittest.mock import Mock, patch

from services import generate_broadcast_analysis
from utils import Article


class TestTTSService:
    """Test suite for TTS service functions."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        mock_client = Mock()
        return mock_client

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
                headline="Climate Summit Reaches Agreement",
                summary="World leaders agree on ambitious climate targets for 2030.",
                story="In a historic moment, global leaders at the Climate Summit have reached a consensus on reducing carbon emissions by 50% by 2030.",
                sources=["https://example.com/climate", "https://example.com/summit"],
                broadcast=b"",  # Placeholder
                reporter=""     # Placeholder
            ),
            Article(
                headline="Tech Innovation Breakthrough",
                summary="New AI technology promises to revolutionize healthcare.",
                story="Researchers have developed an AI system capable of diagnosing diseases with 99% accuracy, marking a significant breakthrough in medical technology.",
                sources=["https://example.com/tech", "https://example.com/ai"],
                broadcast=b"",
                reporter=""
            )
        ]

    def test_generate_broadcast_analysis_success(self, mock_openai_client, mock_mongodb_client, sample_articles):
        """Test successful broadcast analysis generation."""
        # Setup mocks
        mock_openai_client.chat_completion.side_effect = [
            "Professional analysis of the climate summit for broadcast presentation.",
            "Breaking news analysis of the AI breakthrough in healthcare technology."
        ]
        mock_openai_client.text_to_speech.side_effect = [
            b"climate_audio_data",
            b"tech_audio_data"
        ]
        mock_mongodb_client.insert_article.side_effect = ["60a1b2c3d4e5f6789", "60a1b2c3d4e5f6790"]
        
        with patch('services.tts.get_random_REPORTER_VOICE', side_effect=[('ash', 'Alex'), ('ballad', 'Blake')]):
            with patch('services.tts.TTS_INSTRUCTIONS', 'Analyze: {headline} - {summary} - {story}'):
                result = generate_broadcast_analysis(
                    sample_articles,
                    openai_client=mock_openai_client,
                    mongodb_client=mock_mongodb_client
                )
        
        assert len(result) == 2
        
        # Verify first article
        assert result[0].headline == "Climate Summit Reaches Agreement"
        assert result[0].broadcast == b"climate_audio_data"
        assert result[0].reporter == "Alex"
        
        # Verify second article
        assert result[1].headline == "Tech Innovation Breakthrough"
        assert result[1].broadcast == b"tech_audio_data"
        assert result[1].reporter == "Blake"
        
        # Verify OpenAI calls
        assert mock_openai_client.chat_completion.call_count == 2
        assert mock_openai_client.text_to_speech.call_count == 2
        
        # Verify MongoDB calls
        assert mock_mongodb_client.insert_article.call_count == 2

    def test_generate_broadcast_analysis_error_handling(self, mock_openai_client, mock_mongodb_client, sample_articles):
        """Test error handling in broadcast analysis generation."""
        # Chat completion succeeds, TTS fails
        mock_openai_client.chat_completion.return_value = "Analysis text"
        mock_openai_client.text_to_speech.side_effect = Exception("TTS failed")
        
        with patch('services.tts.get_random_REPORTER_VOICE', return_value=('ash', 'Alex')):
            with patch('services.tts.logger') as mock_logger:
                result = generate_broadcast_analysis(
                    [sample_articles[0]],
                    openai_client=mock_openai_client,
                    mongodb_client=mock_mongodb_client
                )
        
        # Should return empty list when TTS fails
        assert len(result) == 0
        mock_logger.error.assert_called_once()
        mock_mongodb_client.insert_article.assert_not_called()

    def test_generate_broadcast_analysis_empty_list(self, mock_openai_client, mock_mongodb_client):
        """Test TTS generation with empty article list."""
        with patch('services.tts.logger') as mock_logger:
            result = generate_broadcast_analysis(
                [],
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )
        
        assert result == []
        mock_openai_client.chat_completion.assert_not_called()
        mock_openai_client.text_to_speech.assert_not_called()
        mock_mongodb_client.insert_article.assert_not_called()
        
        mock_logger.info.assert_called_once_with(
            "Generated broadcasts: %d/%d articles processed", 0, 0
        )

    def test_generate_broadcast_analysis_prompt_formatting(self, mock_openai_client, mock_mongodb_client, sample_articles):
        """Test that analysis prompts are properly formatted."""
        mock_openai_client.chat_completion.return_value = "Analysis"
        mock_openai_client.text_to_speech.return_value = b"audio"
        mock_mongodb_client.insert_article.return_value = "id123"
        
        with patch('services.tts.get_random_REPORTER_VOICE', return_value=('ash', 'Alex')):
            with patch('services.tts.TTS_INSTRUCTIONS', 'Analyze {headline} and {summary} with {story}'):
                generate_broadcast_analysis(
                    [sample_articles[0]],
                    openai_client=mock_openai_client,
                    mongodb_client=mock_mongodb_client
                )
        
        # Verify prompt formatting
        call_args = mock_openai_client.chat_completion.call_args[0][0]
        assert sample_articles[0].headline in call_args
        assert sample_articles[0].summary in call_args
        assert sample_articles[0].story in call_args

    @patch('services.tts.logger')
    def test_logging_tts_service(self, mock_logger, mock_openai_client, mock_mongodb_client, sample_articles):
        """Test that TTS service logs properly."""
        # Mock OpenAI responses
        mock_openai_client.chat_completion.return_value = "Generated reporter analysis"
        mock_openai_client.text_to_speech.return_value = b"fake_audio_data"
        
        # Mock MongoDB insertion
        mock_mongodb_client.insert_article.return_value = "60a1b2c3d4e5f6789"
        
        # Mock voice selection
        with patch('services.tts.get_random_REPORTER_VOICE', return_value=('alloy', 'Alex')):
            generate_broadcast_analysis(
                sample_articles,
                openai_client=mock_openai_client,
                mongodb_client=mock_mongodb_client
            )
        
        # Verify logging calls
        mock_logger.info.assert_any_call(
            "Generating analysis for: '%s'", "Climate Summit Reaches Agreement"
        )
        mock_logger.info.assert_any_call(
            "Selected reporter: %s (%s)", "Alex", "alloy"
        )
        mock_logger.info.assert_any_call(
            "Converting to speech: '%s'", "Climate Summit Reaches Agreement"
        )
        mock_logger.info.assert_called_with(
            "Generated broadcasts: %d/%d articles processed", 2, 2
        ) 