"""Simple client for interacting with the Perplexity API.

The public Perplexity API is currently in beta/private; this client assumes you
have an API key granting access. If not, you can stub the `research` method or
swap for another provider.
"""
from __future__ import annotations

import httpx

from config.settings import PERPLEXITY_API_KEY, RESEARCH_MODEL, SEARCH_CONTEXT_SIZE
from config.prompts import PERPLEXITY_JOURNALIST_SYSTEM_PROMPT
from utils.logger import logger

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
                    "content": PERPLEXITY_JOURNALIST_SYSTEM_PROMPT,
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
