"""Simple client for interacting with the Perplexity API."""

from __future__ import annotations

from typing import cast

import httpx

from config import (
    PERPLEXITY_API_KEY,
)
from config.discovery_config import (
    DISCOVERY_SYSTEM_PROMPT,
    LEAD_DISCOVERY_MODEL,
    SEARCH_CONTEXT_SIZE as DISCOVERY_SEARCH_CONTEXT_SIZE,
    DISCOVERY_TIMEOUT_SECONDS,
)
from config.research_config import (
    LEAD_RESEARCH_MODEL,
    RESEARCH_SYSTEM_PROMPT,
    SEARCH_CONTEXT_SIZE as RESEARCH_SEARCH_CONTEXT_SIZE,
    RESEARCH_TIMEOUT_SECONDS,
)

_PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"


class PerplexityClient:
    """Tiny wrapper around Perplexity's REST API."""

    _DEFAULT_HEADERS = {
        "Content-Type": "application/json",
    }

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize Perplexity client.

        Args:
            api_key: Perplexity API key. If None, uses PERPLEXITY_API_KEY from config.

        Raises:
            ValueError: If no API key is provided and PERPLEXITY_API_KEY is not set.
        """
        if api_key is None:
            api_key = PERPLEXITY_API_KEY
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY is missing, cannot initialise Perplexity client.")
        self._headers = {**self._DEFAULT_HEADERS, "Authorization": f"Bearer {api_key}"}

    # JSON schema for Story structured output as per docs
    _STORY_JSON_SCHEMA = {
        "type": "object",
        "properties": {
            "headline": {"type": "string"},
            "summary": {"type": "string"},
            "body": {"type": "string"},
            "sources": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["headline", "summary", "body", "sources"],
    }

    # JSON schema for Lead Research structured output
    _LEAD_RESEARCH_JSON_SCHEMA = {
        "type": "object",
        "properties": {
            "context": {"type": "string"},
            "sources": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["context", "sources"],
    }

    # JSON schema for Discovery structured output (array of leads)
    _LEAD_JSON_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "tip": {"type": "string"},
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["tip", "sources"],
        },
    }

    # ---------------------------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------------------------

    def lead_research(self, prompt: str) -> str:
        """Executes research for a lead and returns structured JSON.

        Uses structured output for consistent JSON responses.

        Args:
            prompt: The research query/prompt

        Returns:
            JSON string containing the structured research results
        """
        payload = {
            "model": LEAD_RESEARCH_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": RESEARCH_SYSTEM_PROMPT,
                },
                {"role": "user", "content": prompt},
            ],
            "web_search_options": {
                "search_context_size": RESEARCH_SEARCH_CONTEXT_SIZE,
            },
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self._LEAD_RESEARCH_JSON_SCHEMA},
            },
        }

        # Set timeout for research operations that involve web search
        timeout = httpx.Timeout(RESEARCH_TIMEOUT_SECONDS)
        with httpx.Client(timeout=timeout) as client:
            response = client.post(_PERPLEXITY_ENDPOINT, json=payload, headers=self._headers)
            response.raise_for_status()
            data = response.json()

        return cast("str", data["choices"][0]["message"]["content"])

    def lead_discovery(self, prompt: str) -> str:
        """Executes a research for leads.

        Uses structured output for consistent JSON responses.

        This includes
        reasoning tokens wrapped in <think> tags. The response is parsed to
        extract only the JSON content.

        Args:
            prompt: The research query/prompt

        Returns:
            JSON string containing the structured research results
        """
        payload = {
            "model": LEAD_DISCOVERY_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": DISCOVERY_SYSTEM_PROMPT,
                },
                {"role": "user", "content": prompt},
            ],
            "web_search_options": {
                "search_context_size": DISCOVERY_SEARCH_CONTEXT_SIZE,
            },
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self._LEAD_JSON_SCHEMA},
            },
        }

        # Set timeout for discovery operations that involve web search and reasoning
        timeout = httpx.Timeout(DISCOVERY_TIMEOUT_SECONDS)
        with httpx.Client(timeout=timeout) as client:
            response = client.post(_PERPLEXITY_ENDPOINT, json=payload, headers=self._headers)
            response.raise_for_status()
            data = response.json()

        # Response contains reasoning tokens in <think> tags followed by JSON
        raw_content: str = data["choices"][0]["message"]["content"]

        # Extract JSON content after <think> section as per documentation
        return self._extract_json_from_reasoning_response(raw_content)

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _extract_json_from_reasoning_response(self, raw_content: str) -> str:
        """Extract JSON from response with reasoning tokens.

        Perplexity Pro models return reasoning tokens in <think> tags,
        followed by the actual JSON response.
        """
        import re

        # Split by </think> to get the JSON part, fallback to entire content if no </think> tag
        json_part = raw_content.split("</think>", 1)[1].strip() if "</think>" in raw_content else raw_content.strip()

        # Clean up any remaining markdown or XML-like tags
        json_part = re.sub(r"```(?:json)?\n?", "", json_part)
        return re.sub(r"\n?```", "", json_part)
