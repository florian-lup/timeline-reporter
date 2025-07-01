"""Voice selection utilities."""

from __future__ import annotations

import random
from config import TTS_VOICE, REPORTER_VOICE


def get_random_tts_voice() -> tuple[str, str]:
    """
    Get a random TTS voice.
    
    Returns:
        tuple[str, str]: A tuple containing (api_name, human_name)
    """
    api_name = random.choice(list(TTS_VOICE.keys()))
    human_name = TTS_VOICE[api_name]
    return api_name, human_name


def get_random_reporter_voice() -> tuple[str, str]:
    """
    Get a random reporter voice.
    
    Returns:
        tuple[str, str]: A tuple containing (api_name, human_name)
    """
    api_name = random.choice(list(REPORTER_VOICE.keys()))
    human_name = REPORTER_VOICE[api_name]
    return api_name, human_name


def get_random_tts_voice_api_name() -> str:
    """
    Get a random TTS voice API name only.
    
    Returns:
        str: The API name for the voice (e.g., "ash")
    """
    return random.choice(list(TTS_VOICE.keys()))


def get_random_reporter_voice_api_name() -> str:
    """
    Get a random reporter voice API name only.
    
    Returns:
        str: The API name for the voice (e.g., "breeze")
    """
    return random.choice(list(REPORTER_VOICE.keys()))


def get_random_tts_voice_human_name() -> str:
    """
    Get a random TTS voice human name only.
    
    Returns:
        str: The human name for the voice (e.g., "Alex")
    """
    api_name = random.choice(list(TTS_VOICE.keys()))
    return TTS_VOICE[api_name]


def get_random_reporter_voice_human_name() -> str:
    """
    Get a random reporter voice human name only.
    
    Returns:
        str: The human name for the voice (e.g., "Brian")
    """
    api_name = random.choice(list(REPORTER_VOICE.keys()))
    return REPORTER_VOICE[api_name] 