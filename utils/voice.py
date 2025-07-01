"""Voice selection utilities."""

from __future__ import annotations

import random
from config import REPORTER_VOICE, HOST_VOICE


def get_random_REPORTER_VOICE() -> tuple[str, str]:
    """
    Get a random TTS voice.
    
    Returns:
        tuple[str, str]: A tuple containing (api_name, human_name)
    """
    api_name = random.choice(list(REPORTER_VOICE.keys()))
    human_name = REPORTER_VOICE[api_name]
    return api_name, human_name


def get_random_HOST_VOICE() -> tuple[str, str]:
    """
    Get a random reporter voice.
    
    Returns:
        tuple[str, str]: A tuple containing (api_name, human_name)
    """
    api_name = random.choice(list(HOST_VOICE.keys()))
    human_name = HOST_VOICE[api_name]
    return api_name, human_name


def get_random_REPORTER_VOICE_api_name() -> str:
    """
    Get a random TTS voice API name only.
    
    Returns:
        str: The API name for the voice (e.g., "ash")
    """
    return random.choice(list(REPORTER_VOICE.keys()))


def get_random_HOST_VOICE_api_name() -> str:
    """
    Get a random reporter voice API name only.
    
    Returns:
        str: The API name for the voice (e.g., "breeze")
    """
    return random.choice(list(HOST_VOICE.keys()))


def get_random_REPORTER_VOICE_human_name() -> str:
    """
    Get a random TTS voice human name only.
    
    Returns:
        str: The human name for the voice (e.g., "Alex")
    """
    api_name = random.choice(list(REPORTER_VOICE.keys()))
    return REPORTER_VOICE[api_name]


def get_random_HOST_VOICE_human_name() -> str:
    """
    Get a random reporter voice human name only.
    
    Returns:
        str: The human name for the voice (e.g., "Brian")
    """
    api_name = random.choice(list(HOST_VOICE.keys()))
    return HOST_VOICE[api_name] 