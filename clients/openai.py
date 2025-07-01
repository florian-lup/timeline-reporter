"""Wrapper around the OpenAI SDK used by this project."""
from __future__ import annotations

from typing import List

import openai
from openai import OpenAI

from config import (
    EMBEDDING_DIMENSIONS, 
    EMBEDDING_MODEL, 
    OPENAI_API_KEY,
    TTS_MODEL,
)
from utils import logger


class OpenAIClient:
    """Lightweight wrapper around the OpenAI Python SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing, cannot initialise OpenAI client.")

        self._client = OpenAI(api_key=api_key)

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def chat_completion(self, prompt: str, *, model: str, temperature: float = None) -> str:
        """Generate text using the chat completion model.
        
        Args:
            prompt: The input prompt for text generation
            model: Model to use for completion
            temperature: Sampling temperature 0-2 (optional)
            
        Returns:
            The generated text response
        """
        logger.info("Generating chat completion (length: %d chars, model: %s)", len(prompt), model)
        
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if temperature is not None:
            kwargs["temperature"] = temperature
        
        response = self._client.chat.completions.create(**kwargs)  # type: ignore[attr-defined]
        
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
