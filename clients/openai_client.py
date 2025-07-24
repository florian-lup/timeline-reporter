"""Wrapper around the OpenAI SDK used by this project."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from config import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
)
from config.audio_config import TTS_MODEL, TTS_SPEED, TTS_VOICE, TTSVoice, AUDIO_FORMAT


class OpenAIClient:
    """Lightweight wrapper around the OpenAI Python SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY from config.

        Raises:
            ValueError: If no API key is provided and OPENAI_API_KEY is not set.
        """
        if api_key is None:
            api_key = OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing, cannot initialise OpenAI client.")

        self._client = OpenAI(api_key=api_key)

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def chat_completion(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float | None = None,
        response_format: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Generate text using the chat completion model.

        Args:
            prompt: The input prompt for text generation
            model: Model to use for completion
            temperature: Sampling temperature 0-2 (optional)
            response_format: Response format specification (optional)
            system_prompt: System prompt to set behavior (optional)

        Returns:
            The generated text response
        """
        messages = []
        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        if temperature is not None:
            kwargs["temperature"] = temperature

        if response_format is not None:
            kwargs["response_format"] = response_format

        response = self._client.chat.completions.create(**kwargs)

        content: str = response.choices[0].message.content
        return content

    def embed_text(self, text: str) -> list[float]:
        """Gets an embedding vector for *text*."""
        response = self._client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL,
            dimensions=EMBEDDING_DIMENSIONS,
        )
        vector: list[float] = response.data[0].embedding
        return vector

    def text_to_speech(
        self,
        text: str,
        *,
        model: str = TTS_MODEL,
        voice: TTSVoice = TTS_VOICE,
        speed: float = TTS_SPEED,
        response_format: str = AUDIO_FORMAT,
        instruction: str | None = None,
    ) -> bytes:
        """Convert text to speech using OpenAI TTS.

        Args:
            text: The text to convert to speech
            model: TTS model to use (default from config: TTS_MODEL)
            voice: Voice to use (default from config: TTS_VOICE)
            speed: Speech speed (default from config: TTS_SPEED)
            response_format: Audio format (mp3, opus, aac, flac)
            instruction: TTS instruction for enhanced voice control (gpt-4o-mini-tts only)

        Returns:
            Audio data as bytes
        """
        # Prepare request parameters
        request_params = {
            "model": model,
            "voice": voice,
            "input": text,
            "speed": speed,
            "response_format": response_format,
        }
        
        # Add instruction parameter for gpt-4o-mini-tts model
        if instruction is not None and "gpt-4o-mini-tts" in model:
            request_params["instructions"] = instruction
        
        response = self._client.audio.speech.create(**request_params)
        return response.content
