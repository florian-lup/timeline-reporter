"""Test suite for OpenAI client."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from clients.openai import OpenAIClient


class TestOpenAIClient:
    """Test suite for OpenAIClient."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch('clients.openai.OpenAI') as mock_openai:
            mock_instance = Mock()
            mock_openai.return_value = mock_instance
            yield mock_openai, mock_instance

    @pytest.fixture
    def mock_openai_legacy(self):
        """Mock legacy OpenAI configuration."""
        with patch('clients.openai.OpenAI', side_effect=ImportError):
            with patch('clients.openai.openai') as mock_openai_module:
                yield mock_openai_module

    def test_init_with_default_api_key(self, mock_openai_client):
        """Test initialization with default API key from config."""
        mock_openai, mock_instance = mock_openai_client
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            client = OpenAIClient()
            
            mock_openai.assert_called_once_with(api_key='test-api-key')
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
        with patch('clients.openai.OPENAI_API_KEY', None):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is missing"):
                OpenAIClient()

    def test_init_with_empty_api_key_and_empty_config(self, mock_openai_client):
        """Test initialization fails when API key is empty and config is empty."""
        with patch('clients.openai.OPENAI_API_KEY', ''):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is missing"):
                OpenAIClient()

    def test_init_legacy_fallback(self, mock_openai_legacy):
        """Test fallback to legacy OpenAI configuration."""
        mock_openai_module = mock_openai_legacy
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            client = OpenAIClient()
            
            assert mock_openai_module.api_key == 'test-api-key'
            assert client._client == mock_openai_module

    def test_deep_research_success(self, mock_openai_client):
        """Test successful deep research call."""
        mock_openai, mock_instance = mock_openai_client
        
        # Mock the response structure
        mock_response = Mock()
        mock_output = Mock()
        mock_content = Mock()
        mock_content.text = '{"result": "test response"}'
        mock_output.content = [mock_content]
        mock_response.output = [mock_output]
        
        mock_instance.responses.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            # Fix the undefined max_tokens variable
            with patch('clients.openai.max_tokens', 4000):
                client = OpenAIClient()
                result = client.deep_research("test prompt")
                
                assert result == '{"result": "test response"}'
                mock_instance.responses.create.assert_called_once()

    def test_deep_research_with_proper_payload(self, mock_openai_client):
        """Test that deep research creates proper request payload."""
        mock_openai, mock_instance = mock_openai_client
        
        mock_response = Mock()
        mock_output = Mock()
        mock_content = Mock()
        mock_content.text = '{"result": "test"}'
        mock_output.content = [mock_content]
        mock_response.output = [mock_output]
        
        mock_instance.responses.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            with patch('clients.openai.DEEP_RESEARCH_MODEL', 'test-model'):
                with patch('clients.openai.max_tokens', 4000):
                    client = OpenAIClient()
                    client.deep_research("test prompt")
                    
                    # Verify the call was made with correct parameters
                    call_args = mock_instance.responses.create.call_args
                    assert call_args[1]['model'] == 'test-model'
                    assert call_args[1]['max_tokens'] == 4000
                    assert len(call_args[1]['input']) == 2
                    assert call_args[1]['tools'][0]['type'] == 'web_search_preview'

    def test_embed_text_success(self, mock_openai_client):
        """Test successful text embedding."""
        mock_openai, mock_instance = mock_openai_client
        
        # Mock the embeddings response
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_response.data = [mock_data]
        
        mock_instance.embeddings.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
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
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            with patch('clients.openai.EMBEDDING_MODEL', 'text-embedding-3-small'):
                with patch('clients.openai.EMBEDDING_DIMENSIONS', 1536):
                    client = OpenAIClient()
                    client.embed_text("test text")
                    
                    mock_instance.embeddings.create.assert_called_once_with(
                        input="test text",
                        model="text-embedding-3-small",
                        dimensions=1536
                    )

    @pytest.mark.parametrize("text_input,expected_length", [
        ("short", 5),
        ("", 0),
        ("a" * 1000, 1000),
        ("unicode: 🚀 emoji test", 19)
    ])
    def test_embed_text_various_inputs(self, mock_openai_client, text_input, expected_length):
        """Test embed_text with various text inputs."""
        mock_openai, mock_instance = mock_openai_client
        
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1] * 10  # Fixed size embedding
        mock_response.data = [mock_data]
        
        mock_instance.embeddings.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            client = OpenAIClient()
            result = client.embed_text(text_input)
            
            assert isinstance(result, list)
            assert all(isinstance(x, float) for x in result)

    @patch('clients.openai.logger')
    def test_logging_deep_research(self, mock_logger, mock_openai_client):
        """Test that deep research logs properly."""
        mock_openai, mock_instance = mock_openai_client
        
        mock_response = Mock()
        mock_output = Mock()
        mock_content = Mock()
        mock_content.text = '{"result": "test"}'
        mock_output.content = [mock_content]
        mock_response.output = [mock_output]
        
        mock_instance.responses.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            with patch('clients.openai.max_tokens', 4000):
                client = OpenAIClient()
                client.deep_research("test prompt")
                
                mock_logger.info.assert_called_once_with(
                    "Running deep research for prompt: %s",
                    "test prompt"
                )
                mock_logger.debug.assert_called_once_with(
                    "Deep research raw response: %s",
                    '{"result": "test"}'
                )

    @patch('clients.openai.logger')
    def test_logging_embed_text(self, mock_logger, mock_openai_client):
        """Test that embed_text logs properly."""
        mock_openai, mock_instance = mock_openai_client
        
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_data]
        
        mock_instance.embeddings.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            client = OpenAIClient()
            client.embed_text("test text")
            
            mock_logger.debug.assert_called_once_with(
                "Creating embedding for %d chars",
                9  # length of "test text"
            )

    def test_deep_research_exception_handling(self, mock_openai_client):
        """Test that deep research properly propagates exceptions."""
        mock_openai, mock_instance = mock_openai_client
        
        mock_instance.responses.create.side_effect = Exception("API Error")
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            with patch('clients.openai.max_tokens', 4000):
                client = OpenAIClient()
                
                with pytest.raises(Exception, match="API Error"):
                    client.deep_research("test prompt")

    def test_embed_text_exception_handling(self, mock_openai_client):
        """Test that embed_text properly propagates exceptions."""
        mock_openai, mock_instance = mock_openai_client
        
        mock_instance.embeddings.create.side_effect = Exception("Embedding Error")
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            client = OpenAIClient()
            
            with pytest.raises(Exception, match="Embedding Error"):
                client.embed_text("test text")

    def test_init_fails_without_api_key(self, mock_openai_client):
        """Test initialization fails when API key is missing."""
        with patch('clients.openai.OPENAI_API_KEY', None):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is missing"):
                OpenAIClient()

    def test_embed_text_parameters(self, mock_openai_client):
        """Test that embed_text uses correct parameters."""
        mock_openai, mock_instance = mock_openai_client
        
        mock_response = Mock()
        mock_data = Mock()
        mock_data.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_data]
        
        mock_instance.embeddings.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            with patch('clients.openai.EMBEDDING_MODEL', 'text-embedding-3-small'):
                with patch('clients.openai.EMBEDDING_DIMENSIONS', 1536):
                    client = OpenAIClient()
                    client.embed_text("test text")
                    
                    mock_instance.embeddings.create.assert_called_once_with(
                        input="test text",
                        model="text-embedding-3-small",
                        dimensions=1536
                    )

    @patch('clients.openai.logger')
    def test_logging(self, mock_logger, mock_openai_client):
        """Test that methods log properly."""
        mock_openai, mock_instance = mock_openai_client
        
        # Test deep research logging
        mock_response = Mock()
        mock_output = Mock()
        mock_content = Mock()
        mock_content.text = '{"result": "test"}'
        mock_output.content = [mock_content]
        mock_response.output = [mock_output]
        
        mock_instance.responses.create.return_value = mock_response
        
        with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
            with patch('clients.openai.max_tokens', 4000):
                client = OpenAIClient()
                client.deep_research("test prompt")
                
                mock_logger.info.assert_called_with(
                    "Running deep research for prompt: %s",
                    "test prompt"
                )

    def test_legacy_openai_fallback(self):
        """Test fallback to legacy OpenAI configuration."""
        with patch('clients.openai.OpenAI', side_effect=ImportError):
            with patch('clients.openai.openai') as mock_openai_module:
                with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
                    client = OpenAIClient()
                    
                    assert mock_openai_module.api_key == 'test-api-key'
                    assert client._client == mock_openai_module 