"""Test suite for Perplexity client."""

import json
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from clients import PerplexityClient


class TestPerplexityClient:
    """Test suite for PerplexityClient."""

    @pytest.fixture
    def sample_response_data(self):
        """Sample API response data."""
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "headline": "Test Headline",
                                "summary": "Test summary",
                                "body": "Test story content",
                                "sources": [
                                    "https://example.com/source1",
                                    "https://example.com/source2",
                                ],
                            }
                        )
                    }
                }
            ]
        }

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx.Client."""
        with patch("clients.perplexity_client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            yield mock_client, mock_response

    def test_init_with_default_api_key(self):
        """Test initialization with default API key from config."""
        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()

            expected_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer test-api-key",
            }
            assert client._headers == expected_headers

    def test_init_with_custom_api_key(self):
        """Test initialization with custom API key."""
        custom_key = "custom-api-key"
        client = PerplexityClient(api_key=custom_key)

        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {custom_key}",
        }
        assert client._headers == expected_headers

    def test_init_with_none_api_key_and_missing_config(self):
        """Test initialization fails when API key is None and config is missing."""
        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", None),
            pytest.raises(ValueError, match="PERPLEXITY_API_KEY is missing"),
        ):
            PerplexityClient()

    def test_init_with_empty_api_key_and_empty_config(self):
        """Test initialization fails when API key is empty and config is empty."""
        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", ""),
            pytest.raises(ValueError, match="PERPLEXITY_API_KEY is missing"),
        ):
            PerplexityClient()

    def test_init_with_explicit_none_api_key_and_missing_config(self):
        """Test initialization fails when API key is explicitly None.

        Should fail when config is missing.
        """
        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", None),
            pytest.raises(ValueError, match="PERPLEXITY_API_KEY is missing"),
        ):
            PerplexityClient(api_key=None)

    def test_research_success(self, mock_httpx_client, sample_response_data):
        """Test successful research call."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            result = client.lead_research("test prompt")

            expected_content = json.dumps(
                {
                    "headline": "Test Headline",
                    "summary": "Test summary",
                    "body": "Test story content",
                    "sources": [
                        "https://example.com/source1",
                        "https://example.com/source2",
                    ],
                }
            )
            assert result == expected_content

    def test_research_request_structure(self, mock_httpx_client, sample_response_data):
        """Test that research creates proper request structure."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch("clients.perplexity_client.LEAD_RESEARCH_MODEL", "test-model"),
            patch("clients.perplexity_client.SEARCH_CONTEXT_SIZE", "large"),
        ):
            client = PerplexityClient()
            client.lead_research("test prompt")

            # Verify the POST call
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args

            # Check URL
            assert call_args[0][0] == "https://api.perplexity.ai/chat/completions"

            # Check headers
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"
            assert call_args[1]["headers"]["Content-Type"] == "application/json"

            # Check payload structure
            payload = call_args[1]["json"]
            assert payload["model"] == "test-model"
            assert len(payload["messages"]) == 2
            assert payload["messages"][0]["role"] == "system"
            assert payload["messages"][1]["role"] == "user"
            assert payload["messages"][1]["content"] == "test prompt"
            assert payload["web_search_options"]["search_context_size"] == "large"
            assert payload["response_format"]["type"] == "json_schema"

    def test_research_json_schema_structure(
        self, mock_httpx_client, sample_response_data
    ):
        """Test that the JSON schema is properly structured."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            client.lead_research("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            schema = payload["response_format"]["json_schema"]["schema"]

            # Verify schema structure
            assert schema["type"] == "object"
            assert "properties" in schema
            assert "required" in schema

            # Verify required fields
            required_fields = ["headline", "summary", "body", "sources"]
            assert set(schema["required"]) == set(required_fields)

            # Verify properties
            for field in required_fields:
                assert field in schema["properties"]

            # Verify sources is array of strings
            sources_prop = schema["properties"]["sources"]
            assert sources_prop["type"] == "array"
            assert sources_prop["items"]["type"] == "string"
            # Note: format constraint is optional in JSON schema

    def test_research_http_error(self, mock_httpx_client):
        """Test that HTTP errors are properly raised."""
        mock_client, mock_response = mock_httpx_client
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=Mock()
        )

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()

            with pytest.raises(httpx.HTTPStatusError):
                client.lead_research("test prompt")

    def test_research_timeout_configuration(self, sample_response_data):
        """Test that HTTP client is configured with proper timeout."""
        with patch("clients.perplexity_client.httpx.Client") as mock_client_class:
            mock_context_manager = MagicMock()
            mock_client = Mock()
            mock_response = Mock()

            mock_client_class.return_value = mock_context_manager
            mock_context_manager.__enter__.return_value = mock_client
            mock_context_manager.__exit__.return_value = None

            mock_response.json.return_value = sample_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
                client = PerplexityClient()
                client.lead_research("test prompt")

                # Verify Client was initialized with timeout=90
                mock_client_class.assert_called_with(timeout=90)

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
    def test_research_various_prompts(
        self, mock_httpx_client, sample_response_data, prompt
    ):
        """Test research with various prompt inputs."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            result = client.lead_research(prompt)

            # Verify the prompt was passed correctly
            payload = mock_client.post.call_args[1]["json"]
            assert payload["messages"][1]["content"] == prompt

            # Should return valid JSON content
            assert isinstance(result, str)
            json.loads(result)  # Should not raise exception

    @patch("clients.perplexity_client.logger")
    def test_logging_research(
        self, mock_logger, mock_httpx_client, sample_response_data
    ):
        """Test that research method logs properly."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            client.lead_research("test prompt")

            mock_logger.info.assert_called_once_with(
                "Research request with %s", "sonar-pro"
            )

    def test_system_message_content(self, mock_httpx_client, sample_response_data):
        """Test that system message contains proper instructions."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            client.lead_research("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            system_message = payload["messages"][0]["content"]

            assert "investigative journalist" in system_message
            assert "current events analysis" in system_message
            assert "accuracy" in system_message
            assert "factual reporting" in system_message

    def test_response_content_extraction(self, mock_httpx_client):
        """Test that response content is properly extracted."""
        mock_client, mock_response = mock_httpx_client

        test_content = '{"test": "content"}'
        response_data = {"choices": [{"message": {"content": test_content}}]}

        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            result = client.lead_research("test prompt")

            assert result == test_content

    def test_default_headers_immutability(self):
        """Test that default headers are not modified by instance creation."""
        original_defaults = PerplexityClient._DEFAULT_HEADERS.copy()

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-key-1"):
            client1 = PerplexityClient()

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-key-2"):
            client2 = PerplexityClient()

        # Verify original defaults weren't modified
        assert original_defaults == PerplexityClient._DEFAULT_HEADERS

        # Verify instances have different auth headers
        assert client1._headers["Authorization"] == "Bearer test-key-1"
        assert client2._headers["Authorization"] == "Bearer test-key-2"

    def test_lead_discovery_success(self, mock_httpx_client):
        """Test successful deep research call."""
        mock_client, mock_response = mock_httpx_client

        # Mock response with <think> tags as per documentation
        raw_response = """<think>
I need to find recent events about climate and geopolitical developments.
Let me search for current information.
</think>
[
  {
    "tip": "Climate Summit Reaches Agreement: World leaders at COP29 "
    "reach historic agreement on climate funding."
  },
  {
    "tip": "Geopolitical Tensions Rise: Recent diplomatic developments show "
    "increasing tensions."
  }
]"""

        response_data = {"choices": [{"message": {"content": raw_response}}]}

        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            result = client.lead_discovery(
                "Find recent events about climate and geopolitics"
            )

            # Should extract JSON after <think> section
            expected_json = """[
  {
    "tip": "Climate Summit Reaches Agreement: World leaders at COP29 "
    "reach historic agreement on climate funding."
  },
  {
    "tip": "Geopolitical Tensions Rise: Recent diplomatic developments show "
    "increasing tensions."
  }
]"""
            assert result == expected_json

    def test_lead_discovery_request_structure(self, mock_httpx_client):
        """Test that deep research creates proper request structure."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch(
                "clients.perplexity_client.LEAD_DISCOVERY_MODEL", "sonar-deep-research"
            ),
        ):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            # Verify the POST call
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args

            # Check payload structure
            payload = call_args[1]["json"]
            assert payload["model"] == "sonar-deep-research"
            assert len(payload["messages"]) == 2
            assert payload["messages"][0]["role"] == "system"
            assert payload["messages"][1]["role"] == "user"
            assert payload["messages"][1]["content"] == "test prompt"
            assert payload["response_format"]["type"] == "json_schema"
            assert "web_search_options" in payload
            assert "search_context_size" in payload["web_search_options"]

    def test_lead_discovery_discovery_schema(self, mock_httpx_client):
        """Test that deep research uses the correct discovery JSON schema."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            schema = payload["response_format"]["json_schema"]["schema"]

            # Verify discovery schema structure (array of leads)
            assert schema["type"] == "array"
            assert "items" in schema

            item_schema = schema["items"]
            assert item_schema["type"] == "object"
            assert set(item_schema["required"]) == {"tip"}
            assert "tip" in item_schema["properties"]

    def test_lead_discovery_without_think_tags(self, mock_httpx_client):
        """Test deep research with response that doesn't have <think> tags."""
        mock_client, mock_response = mock_httpx_client

        # Response without <think> tags
        raw_response = """[
  {
    "tip": "Direct Response: This response doesn't have think tags."
  }
]"""

        response_data = {"choices": [{"message": {"content": raw_response}}]}

        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            result = client.lead_discovery("test prompt")

            # Should return the full response as-is
            assert result == raw_response

    def test_lead_discovery_timeout_configuration(self):
        """Test that deep research uses longer timeout (180s)."""
        with patch("clients.perplexity_client.httpx.Client") as mock_client_class:
            mock_context_manager = MagicMock()
            mock_client = Mock()
            mock_response = Mock()

            mock_client_class.return_value = mock_context_manager
            mock_context_manager.__enter__.return_value = mock_client
            mock_context_manager.__exit__.return_value = None

            response_data = {"choices": [{"message": {"content": "[]"}}]}
            mock_response.json.return_value = response_data
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
                client = PerplexityClient()
                client.lead_discovery("test prompt")

                # Verify Client was initialized with timeout=180
                # (longer for deep research)
                mock_client_class.assert_called_with(timeout=180)

    @patch("clients.perplexity_client.logger")
    def test_logging_lead_discovery(self, mock_logger, mock_httpx_client):
        """Test that deep research logs properly."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            mock_logger.info.assert_called_once_with(
                "Deep research request with %s", "sonar-reasoning-pro"
            )

    def test_extract_json_from_reasoning_response_with_think(self):
        """Test the _extract_json_from_reasoning_response method.

        Should work with <think> tags.
        """
        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()

            response_with_think = """<think>
Let me analyze the request and find relevant information.
This is reasoning content that should be removed.
</think>
{"result": "extracted json"}"""

            result = client._extract_json_from_reasoning_response(response_with_think)
            assert result == '{"result": "extracted json"}'

    def test_extract_json_from_reasoning_response_without_think(self):
        """Test the _extract_json_from_reasoning_response method.

        Should work without <think> tags.
        """
        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()

            response_without_think = '{"result": "direct json"}'

            result = client._extract_json_from_reasoning_response(
                response_without_think
            )
            assert result == '{"result": "direct json"}'

    def test_lead_discovery_system_prompt(self, mock_httpx_client):
        """Test that deep research uses appropriate system prompt."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            system_message = payload["messages"][0]["content"]

            # Should contain discovery-specific instructions
            expected_text = (
                "expert research assistant specializing in "
                "identifying significant current events"
            )
            assert expected_text in system_message
            assert "factual" in system_message
            assert "reputable sources" in system_message

    def test_lead_discovery_search_context_size(self, mock_httpx_client):
        """Test that deep research uses the configured search context size."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch("clients.perplexity_client.SEARCH_CONTEXT_SIZE", "large"),
        ):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            web_search_options = payload["web_search_options"]

            # Verify search context size is included and uses configured value
            assert web_search_options["search_context_size"] == "large"
