"""Test suite for OpenAI client."""

from unittest.mock import Mock, patch

import pytest

from clients import OpenAIClient


class TestOpenAIClient:
    """Test suite for OpenAIClient."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch("clients.openai_client.OpenAI") as mock_openai:
            mock_instance = Mock()
            mock_openai.return_value = mock_instance
            yield mock_openai, mock_instance

    def test_init_with_default_api_key(self, mock_openai_client):
        """Test initialization with default API key from config."""
        mock_openai, mock_instance = mock_openai_client

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()

            mock_openai.assert_called_once_with(api_key="test-api-key")
            assert client._client == mock_instance

    def test_init_with_custom_api_key(self, mock_openai_client):
        """Test initialization with custom API key."""
        mock_openai, mock_instance = mock_openai_client
        custom_key = "custom-api-key"

        client = OpenAIClient(api_key=custom_key)

        mock_openai.assert_called_once_with(api_key=custom_key)
        assert client._client == mock_instance

    def test_init_with_none_api_key_and_missing_config(self, mock_openai_client):
        """Test initialization fails when API key is None and config is missing."""
        with (
            patch("clients.openai_client.OPENAI_API_KEY", None),
            pytest.raises(ValueError, match="OPENAI_API_KEY is missing"),
        ):
            OpenAIClient()

    def test_init_with_empty_api_key_and_empty_config(self, mock_openai_client):
        """Test initialization fails when API key is empty and config is empty."""
        with (
            patch("clients.openai_client.OPENAI_API_KEY", ""),
            pytest.raises(ValueError, match="OPENAI_API_KEY is missing"),
        ):
            OpenAIClient()

    def test_embed_text_success(self, mock_openai_client):
        """Test successful text embedding."""
        mock_openai, mock_instance = mock_openai_client

        # Mock the embeddings response
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_response.data = [mock_data]

        mock_instance.embeddings.create.return_value = mock_response

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()
            result = client.embed_text("test text")

            assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_instance.embeddings.create.assert_called_once()

    def test_embed_text_with_proper_parameters(self, mock_openai_client):
        """Test that embed_text uses correct parameters."""
        mock_openai, mock_instance = mock_openai_client

        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_data]

        mock_instance.embeddings.create.return_value = mock_response

        with (
            patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"),
            patch("clients.openai_client.EMBEDDING_MODEL", "text-embedding-3-small"),
            patch("clients.openai_client.EMBEDDING_DIMENSIONS", 1536),
        ):
            client = OpenAIClient()
            client.embed_text("test text")

            mock_instance.embeddings.create.assert_called_once_with(
                input="test text",
                model="text-embedding-3-small",
                dimensions=1536,
            )

    @pytest.mark.parametrize(
        "text_input,expected_length",
        [("short", 5), ("", 0), ("a" * 1000, 1000), ("unicode: 🚀 emoji test", 19)],
    )
    def test_embed_text_various_inputs(
        self, mock_openai_client, text_input, expected_length
    ):
        """Test embed_text with various text inputs."""
        mock_openai, mock_instance = mock_openai_client

        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1] * 10  # Fixed size embedding
        mock_response.data = [mock_data]

        mock_instance.embeddings.create.return_value = mock_response

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()
            result = client.embed_text(text_input)

            assert isinstance(result, list)
            assert all(isinstance(x, float) for x in result)

    def test_embed_text_exception_handling(self, mock_openai_client):
        """Test that embed_text properly propagates exceptions."""
        mock_openai, mock_instance = mock_openai_client

        mock_instance.embeddings.create.side_effect = Exception("Embedding Error")

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()

            with pytest.raises(Exception, match="Embedding Error"):
                client.embed_text("test text")

    def test_init_fails_without_api_key(self, mock_openai_client):
        """Test initialization fails when API key is missing."""
        with (
            patch("clients.openai_client.OPENAI_API_KEY", None),
            pytest.raises(ValueError, match="OPENAI_API_KEY is missing"),
        ):
            OpenAIClient()

    def test_embed_text_parameters(self, mock_openai_client):
        """Test that embed_text uses correct parameters."""
        mock_openai, mock_instance = mock_openai_client

        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_data]

        mock_instance.embeddings.create.return_value = mock_response

        with (
            patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"),
            patch("clients.openai_client.EMBEDDING_MODEL", "text-embedding-3-small"),
            patch("clients.openai_client.EMBEDDING_DIMENSIONS", 1536),
        ):
            client = OpenAIClient()
            client.embed_text("test text")

            mock_instance.embeddings.create.assert_called_once_with(
                input="test text",
                model="text-embedding-3-small",
                dimensions=1536,
            )

    def test_chat_completion_success(self, mock_openai_client):
        """Test successful chat completion call."""
        mock_openai, mock_instance = mock_openai_client

        # Mock the chat completion response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "This is a test response from the chat model."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_instance.chat.completions.create.return_value = mock_response

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()
            result = client.chat_completion("test prompt", model="test-model")

            assert result == "This is a test response from the chat model."
            mock_instance.chat.completions.create.assert_called_once()

    def test_chat_completion_with_proper_parameters(self, mock_openai_client):
        """Test that chat_completion uses correct parameters."""
        mock_openai, mock_instance = mock_openai_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Test response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_instance.chat.completions.create.return_value = mock_response

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()
            client.chat_completion("test prompt", model="gpt-4.1")

            mock_instance.chat.completions.create.assert_called_once_with(
                model="gpt-4.1", messages=[{"role": "user", "content": "test prompt"}]
            )

    @pytest.mark.parametrize(
        "prompt",
        [
            "simple prompt",
            "",
            "very " * 100 + "long prompt",
            "unicode: 🚀 emoji prompt",
            "special chars: !@#$%^&*()",
            "multi\nline\nprompt",
        ],
    )
    def test_chat_completion_various_prompts(self, mock_openai_client, prompt):
        """Test chat_completion with various prompt inputs."""
        mock_openai, mock_instance = mock_openai_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_instance.chat.completions.create.return_value = mock_response

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()
            result = client.chat_completion(prompt, model="test-model")

            assert result == "Response"
            # Verify the prompt was passed correctly
            call_args = mock_instance.chat.completions.create.call_args
            assert call_args[1]["messages"][0]["content"] == prompt

    def test_chat_completion_exception_handling(self, mock_openai_client):
        """Test that chat_completion properly propagates exceptions."""
        mock_openai, mock_instance = mock_openai_client

        mock_instance.chat.completions.create.side_effect = Exception("Chat API Error")

        with patch("clients.openai_client.OPENAI_API_KEY", "test-api-key"):
            client = OpenAIClient()

            with pytest.raises(Exception, match="Chat API Error"):
                client.chat_completion("test prompt", model="test-model")
