"""Voice selection utilities."""

from __future__ import annotations

import random
from typing import Literal, cast

from config import HOST_VOICE, REPORTER_VOICE

# Type aliases for the valid voice names
ReporterVoice = Literal["ash", "ballad", "coral", "sage", "verse"]
HostVoice = Literal["alloy", "echo", "fable", "onyx", "shimmer"]


def get_random_reporter_voice() -> tuple[ReporterVoice, str]:
    """Get a random TTS voice.

    Returns:
        tuple[ReporterVoice, str]: A tuple containing (api_name, human_name)
    """
    api_name = cast("ReporterVoice", random.choice(list(REPORTER_VOICE.keys())))
    human_name = REPORTER_VOICE[api_name]
    return api_name, human_name


def get_random_host_voice() -> tuple[HostVoice, str]:
    """Get a random host voice.

    Returns:
        tuple[HostVoice, str]: A tuple containing (api_name, human_name)
    """
    api_name = cast("HostVoice", random.choice(list(HOST_VOICE.keys())))
    human_name = HOST_VOICE[api_name]
    return api_name, human_name


def get_random_reporter_voice_api_name() -> ReporterVoice:
    """Get a random TTS voice API name only.

    Returns:
        ReporterVoice: The API name for the voice (e.g., "ash")
    """
    return cast("ReporterVoice", random.choice(list(REPORTER_VOICE.keys())))


def get_random_host_voice_api_name() -> HostVoice:
    """Get a random host voice API name only.

    Returns:
        HostVoice: The API name for the voice (e.g., "alloy")
    """
    return cast("HostVoice", random.choice(list(HOST_VOICE.keys())))


def get_random_reporter_voice_human_name() -> str:
    """Get a random TTS voice human name only.

    Returns:
        str: The human name for the voice (e.g., "Alex")
    """
    api_name = cast("ReporterVoice", random.choice(list(REPORTER_VOICE.keys())))
    return REPORTER_VOICE[api_name]


def get_random_host_voice_human_name() -> str:
    """Get a random host voice human name only.

    Returns:
        str: The human name for the voice (e.g., "Brian")
    """
    api_name = cast("HostVoice", random.choice(list(HOST_VOICE.keys())))
    return HOST_VOICE[api_name]
