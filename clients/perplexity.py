"""Simple client for interacting with the Perplexity API.

The public Perplexity API is currently in beta/private; this client assumes you
have an API key granting access. If not, you can stub the `research` method or
swap for another provider.
"""
from __future__ import annotations

import httpx
import re

from config import (
    PERPLEXITY_API_KEY, 
    RESEARCH_MODEL, 
    DEEP_RESEARCH_MODEL,
    SEARCH_CONTEXT_SIZE,
    REASONING_EFFORT,
    RESEARCH_SYSTEM_PROMPT,
    DISCOVERY_SYSTEM_PROMPT,
)
from utils import logger

_PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"


class PerplexityClient:
    """Tiny wrapper around Perplexity's REST API."""

    _DEFAULT_HEADERS = {
        "Content-Type": "application/json",
    }

    def __init__(self, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = PERPLEXITY_API_KEY
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY is missing, cannot initialise Perplexity client.")
        self._headers = {**self._DEFAULT_HEADERS, "Authorization": f"Bearer {api_key}"}

    # JSON schema for Article structured output as per docs
    _ARTICLE_JSON_SCHEMA = {
        "type": "object",
        "properties": {
            "headline": {"type": "string"},
            "summary": {"type": "string"},
            "story": {"type": "string"},
            "sources": {
                "type": "array",
                "items": {"type": "string", "format": "uri"},
            },
        },
        "required": ["headline", "summary", "story", "sources"],
    }

    # JSON schema for Discovery structured output (array of events)
    _DISCOVERY_JSON_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": ["title", "summary"],
        },
    }

    def research(self, prompt: str) -> str:
        """Executes a chat completion request forcing JSON structured output.

        Utilises Perplexity's `response_format` parameter (see official guide:
        https://docs.perplexity.ai/guides/structured-outputs) to guarantee the
        model returns a valid JSON object matching the article schema.
        """

        logger.info("Calling Perplexity research endpoint with structured output…")

        payload = {
            "model": RESEARCH_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": RESEARCH_SYSTEM_PROMPT,
                },
                {"role": "user", "content": prompt},
            ],
            "web_search_options": {
                "search_context_size": SEARCH_CONTEXT_SIZE,
            },
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self._ARTICLE_JSON_SCHEMA},
            },
        }

        with httpx.Client(timeout=90) as client:
            response = client.post(_PERPLEXITY_ENDPOINT, json=payload, headers=self._headers)
            response.raise_for_status()
            data = response.json()

        # Response is OpenAI-compatible; content is pure JSON string.
        content: str = data["choices"][0]["message"]["content"]
        return content

    def deep_research(self, prompt: str) -> str:
        """Executes deep research using sonar-deep-research model with structured output.
        
        This method uses the sonar-deep-research model which includes reasoning tokens
        wrapped in <think> tags. The response is parsed to extract only the JSON content.
        
        Args:
            prompt: The research query/prompt
            
        Returns:
            JSON string containing the structured research results
        """
        logger.info("Calling Perplexity deep research endpoint with structured output…")

        payload = {
            "model": DEEP_RESEARCH_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": DISCOVERY_SYSTEM_PROMPT,
                },
                {"role": "user", "content": prompt},
            ],
            "web_search_options": {
                "search_context_size": SEARCH_CONTEXT_SIZE,
            },
            "reasoning_effort": REASONING_EFFORT,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self._DISCOVERY_JSON_SCHEMA},
            },
        }

        with httpx.Client(timeout=180) as client:  # Longer timeout for deep research
            response = client.post(_PERPLEXITY_ENDPOINT, json=payload, headers=self._headers)
            response.raise_for_status()
            data = response.json()

        # Response contains reasoning tokens in <think> tags followed by JSON
        raw_content: str = data["choices"][0]["message"]["content"]
        
        # Extract JSON content after <think> section as per documentation
        content = self._extract_json_from_reasoning_response(raw_content)
        return content

    def _extract_json_from_reasoning_response(self, response: str) -> str:
        """Extract JSON content from a reasoning model response.
        
        Reasoning models like sonar-deep-research wrap their reasoning in <think> tags
        followed by the actual structured output. This method extracts just the JSON.
        
        Args:
            response: Raw response from the reasoning model
            
        Returns:
            JSON string without the <think> section
        """
        # Look for the end of the <think> section
        think_end = response.find("</think>")
        if think_end != -1:
            # Extract everything after </think>
            json_content = response[think_end + 8:].strip()
            logger.debug("Extracted JSON after <think> section: %s", json_content[:200] + "...")
            return json_content
        else:
            # Fallback: if no <think> tags found, return the full response
            logger.warning("No <think> tags found in response, returning full content")
            return response.strip()
