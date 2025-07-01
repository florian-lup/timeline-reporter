"""Wrapper around the OpenAI SDK used by this project."""
from __future__ import annotations

from typing import List

import openai

from config.settings import (
    DEEP_RESEARCH_MODEL, 
    EMBEDDING_DIMENSIONS, 
    EMBEDDING_MODEL, 
    OPENAI_API_KEY,
    TTS_MODEL,
    CHAT_MODEL
)
from config.prompts import OPENAI_DEEP_RESEARCH_SYSTEM_PROMPT
from utils import logger

# Import OpenAI at module level so tests can mock it
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # For older versions of openai package


class OpenAIClient:
    """Lightweight wrapper around the OpenAI Python SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing, cannot initialise OpenAI client.")

        # Newer `openai` package (>=1.0) exposes an explicit client class but we
        # gracefully fallback for older versions.
        if OpenAI is not None:
            try:
                self._client = OpenAI(api_key=api_key)
            except ImportError:
                # Fall back to legacy configuration if OpenAI constructor fails
                openai.api_key = api_key  # type: ignore[attr-defined]
                self._client = openai  # type: ignore
        else:
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
            input=[
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": OPENAI_DEEP_RESEARCH_SYSTEM_PROMPT,
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

    def chat_completion(self, prompt: str) -> str:
        """Generate text using the chat completion model.
        
        Args:
            prompt: The input prompt for text generation
            
        Returns:
            The generated text response
        """
        logger.info("Generating chat completion for prompt (length: %d chars)", len(prompt))
        
        response = self._client.chat.completions.create(  # type: ignore[attr-defined]
            model=CHAT_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        content: str = response.choices[0].message.content  # type: ignore
        logger.debug("Chat completion response: %s", content)
        return content

    def text_to_speech(self, text: str, voice: str) -> bytes:
        """Convert text to speech using OpenAI's TTS model.
        
        Args:
            text: The text to convert to speech
            voice: The voice to use (e.g., "alloy", "echo", "fable", etc.)
            
        Returns:
            MP3 audio data as bytes
        """
        logger.info("Converting text to speech (length: %d chars, voice: %s)", len(text), voice)
        
        response = self._client.audio.speech.create(  # type: ignore[attr-defined]
            model=TTS_MODEL,
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        audio_data: bytes = response.content  # type: ignore
        logger.debug("Generated audio data (size: %d bytes)", len(audio_data))
        return audio_data

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
