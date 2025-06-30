"""Wrapper around the OpenAI SDK used by this project."""
from __future__ import annotations

from typing import List

import openai

from config import DEEP_RESEARCH_MODEL, EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, OPENAI_API_KEY
from utils.logger import logger


class OpenAIClient:
    """Lightweight wrapper around the OpenAI Python SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing, cannot initialise OpenAI client.")

        # Newer `openai` package (>=1.0) exposes an explicit client class but we
        # gracefully fallback for older versions.
        try:
            from openai import OpenAI  # type: ignore

            self._client = OpenAI(api_key=api_key)
        except ImportError:
            # Old style – global configuration.
            openai.api_key = api_key  # type: ignore[attr-defined]
            self._client = openai  # type: ignore

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def deep_research(self, topic_prompt: str) -> str:
        """Runs the deep-research model with a user-supplied prompt.

        The low-level response is returned (i.e. the string content). Parsing is
        left to callers since the desired structure differs per call site.
        """

        logger.info("Running deep research for prompt: %s", topic_prompt)

        # Using the responses endpoint for deep research models
        response = self._client.responses.create(  # type: ignore[attr-defined]
            model=DEEP_RESEARCH_MODEL,
            max_tokens=max_tokens,  # Add token limit to reduce TPM usage
            input=[
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are an expert research assistant. Compile structured, "
                                "factual results only from reputable sources. Provide your answer strictly as JSON with the following format:\n\n"
                                "[\n  {\n    \"title\": <short headline>,\n    \"summary\": <~300 word summary>\n  }\n]\n\n"
                                "Do not include any additional keys, commentary, or markdown."
                            ),
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": topic_prompt,
                        }
                    ]
                }
            ],
            tools=[
                {
                    "type": "web_search_preview"
                }
            ]
        )

        # Extract content from the final output
        content: str = response.output[-1].content[0].text  # type: ignore
        logger.debug("Deep research raw response: %s", content)
        return content

    def embed_text(self, text: str) -> List[float]:
        """Gets an embedding vector for *text*."""
        logger.debug("Creating embedding for %d chars", len(text))

        response = self._client.embeddings.create(  # type: ignore[attr-defined]
            input=text,
            model=EMBEDDING_MODEL,
            dimensions=EMBEDDING_DIMENSIONS,
        )
        vector: List[float] = response.data[0].embedding  # type: ignore
        return vector
