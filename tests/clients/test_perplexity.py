"""Test suite for Perplexity client."""

import json
from unittest.mock import Mock, patch

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
                        "content": "This is the research content for testing purposes."
                    }
                }
            ],
            "search_results": [
                {"url": "https://example.com/source1"},
                {"url": "https://example.com/source2"}
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
            content, citations = client.lead_research("test prompt")

            expected_content = "This is the research content for testing purposes."
            expected_citations = ["https://example.com/source1", "https://example.com/source2"]
            
            assert content == expected_content
            assert citations == expected_citations

    def test_research_request_structure(self, mock_httpx_client, sample_response_data):
        """Test that research creates proper request structure."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch("clients.perplexity_client.LEAD_RESEARCH_MODEL", "test-model"),
            patch("clients.perplexity_client.RESEARCH_SEARCH_CONTEXT_SIZE", "large"),
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
            assert payload["return_citations"] == True

    def test_research_search_context_size(self, mock_httpx_client, sample_response_data):
        """Test that the search context size is properly set."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch("clients.perplexity_client.RESEARCH_SEARCH_CONTEXT_SIZE", "medium"),
        ):
            client = PerplexityClient()
            client.lead_research("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            assert payload["web_search_options"]["search_context_size"] == "medium"

    def test_research_http_error(self, mock_httpx_client):
        """Test that HTTP errors are properly raised."""
        mock_client, mock_response = mock_httpx_client
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404 Not Found", request=Mock(), response=Mock())

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()

            with pytest.raises(httpx.HTTPStatusError):
                client.lead_research("test prompt")

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
    def test_research_various_prompts(self, mock_httpx_client, sample_response_data, prompt):
        """Test research with various prompt inputs."""
        mock_client, mock_response = mock_httpx_client
        mock_response.json.return_value = sample_response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            content, citations = client.lead_research(prompt)

            # Verify the prompt was passed correctly
            payload = mock_client.post.call_args[1]["json"]
            assert payload["messages"][1]["content"] == prompt

            # Should return content as string
            assert isinstance(content, str)
            # Should return citations as list
            assert isinstance(citations, list)

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

            assert "senior investigative research analyst" in system_message
            assert "authoritative sources" in system_message
            # The background keyword is no longer present in the system message
            assert "fact-checking" in system_message

    def test_response_content_extraction(self, mock_httpx_client):
        """Test that response content is properly extracted."""
        mock_client, mock_response = mock_httpx_client

        test_content = '{"test": "content"}'
        response_data = {"choices": [{"message": {"content": test_content}}]}

        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            content, citations = client.lead_research("test prompt")

            assert content == test_content

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
    "discovered_lead": "Climate Summit Reaches Agreement: World leaders at COP29 "
    "successfully negotiate binding carbon reduction targets with developing "
    "nations committing to renewable energy transition timelines."
  },
  {
    "discovered_lead": "Geopolitical Tensions Rise: Recent diplomatic developments show "
    "escalating tensions between major powers as trade negotiations stall "
    "amid concerns over technology transfer restrictions."
  }
]"""

        response_data = {"choices": [{"message": {"content": raw_response}}]}

        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"):
            client = PerplexityClient()
            result = client.lead_discovery("Find recent events about climate and geopolitics")

            # Should extract JSON after <think> section
            expected_json = """[
  {
    "discovered_lead": "Climate Summit Reaches Agreement: World leaders at COP29 "
    "successfully negotiate binding carbon reduction targets with developing "
    "nations committing to renewable energy transition timelines."
  },
  {
    "discovered_lead": "Geopolitical Tensions Rise: Recent diplomatic developments show "
    "escalating tensions between major powers as trade negotiations stall "
    "amid concerns over technology transfer restrictions."
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
            patch("clients.perplexity_client.LEAD_DISCOVERY_MODEL", "sonar-reasoning-pro"),
        ):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            # Verify the POST call
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args

            # Check payload structure
            payload = call_args[1]["json"]
            assert payload["model"] == "sonar-reasoning-pro"
            assert len(payload["messages"]) == 2
            assert payload["messages"][0]["role"] == "system"
            assert payload["messages"][1]["role"] == "user"
            assert payload["messages"][1]["content"] == "test prompt"
            assert payload["response_format"]["type"] == "json_schema"
            assert "web_search_options" in payload
            assert "search_context_size" in payload["web_search_options"]

    def test_lead_discovery_discovery_schema(self, mock_httpx_client):
        """Test that discovery uses the correct discovery JSON schema."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch("clients.perplexity_client.LEAD_DISCOVERY_JSON_SCHEMA", {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "discovered_lead": {
                            "type": "string",
                            "description": "A concise description of the discovered lead"
                        }
                    },
                    "required": ["discovered_lead"]
                }
            })
        ):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            schema = payload["response_format"]["json_schema"]["schema"]

            # Verify discovery schema structure (array of leads)
            assert schema["type"] == "array"
            assert "items" in schema

            item_schema = schema["items"]
            assert item_schema["type"] == "object"
            assert set(item_schema["required"]) == {"discovered_lead"}
            assert "discovered_lead" in item_schema["properties"]

    def test_lead_discovery_without_think_tags(self, mock_httpx_client):
        """Test deep research with response that doesn't have <think> tags."""
        mock_client, mock_response = mock_httpx_client

        # Response without <think> tags
        raw_response = """[
  {
                    "discovered_lead": "Direct Response: This response doesn't have think tags."
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

    def test_extract_json_with_think(self):
        """Test the _extract_json method.

        When the response contains <think> tags, it should extract
        the JSON content that comes after the </think> tag.
        """
        client = PerplexityClient(api_key="fake-api-key")
        response_with_think = """
        <think>Some reasoning here</think>
        [{"discovered_lead": "Test lead"}]
        """
        result = client._extract_json(response_with_think)
        assert result == '[{"discovered_lead": "Test lead"}]'

    def test_extract_json_without_think(self):
        """Test the _extract_json method.

        When the response doesn't contain <think> tags,
        it should still clean up whitespace and formatting.
        """
        client = PerplexityClient(api_key="fake-api-key")
        response_without_think = """
        [{"discovered_lead": "Direct response"}]
        """
        result = client._extract_json(response_without_think)
        assert result == '[{"discovered_lead": "Direct response"}]'

    def test_lead_discovery_system_prompt(self, mock_httpx_client):
        """Test that discovery uses appropriate system prompt."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch("clients.perplexity_client.DISCOVERY_SYSTEM_PROMPT", "You are an investigative news scout for a global newsroom")
        ):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            system_message = payload["messages"][0]["content"]

            # Should contain discovery-specific instructions
            assert "investigative news scout" in system_message

    def test_lead_discovery_search_context_size(self, mock_httpx_client):
        """Test that deep research uses the configured search context size."""
        mock_client, mock_response = mock_httpx_client

        response_data = {"choices": [{"message": {"content": "[]"}}]}
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None

        with (
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-api-key"),
            patch("clients.perplexity_client.DISCOVERY_SEARCH_CONTEXT_SIZE", "large"),
        ):
            client = PerplexityClient()
            client.lead_discovery("test prompt")

            payload = mock_client.post.call_args[1]["json"]
            web_search_options = payload["web_search_options"]

            # Verify search context size is included and uses configured value
            assert web_search_options["search_context_size"] == "large"
