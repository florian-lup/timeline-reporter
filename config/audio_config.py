"""Centralized configuration for audio generation system.

This module contains all settings, prompts, and configuration data
related to podcast/audio generation from story summaries.
"""

from typing import Literal

# ---------------------------------------------------------------------------
# Audio Model Configuration
# ---------------------------------------------------------------------------

# Type alias for valid OpenAI TTS voices
TTSVoice = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

ANCHOR_SCRIPT_MODEL: str = "gpt-4.1-mini-2025-04-14"  # For generating anchor scripts
TTS_MODEL: str = "gpt-4o-mini-tts"  # OpenAI TTS model
TTS_VOICE: TTSVoice = "alloy"  # Voice selection: alloy, echo, fable, onyx, nova, shimmer
TTS_SPEED: float = 1.0  # Speed: 0.25 to 4.0

# ---------------------------------------------------------------------------
# Audio File Configuration
# ---------------------------------------------------------------------------
AUDIO_FORMAT: str = "mp3"

# ---------------------------------------------------------------------------
# Anchor Script System Prompt
# ---------------------------------------------------------------------------
ANCHOR_SCRIPT_SYSTEM_PROMPT = """
You are a professional news anchor for a major broadcasting network, writing scripts for 
a daily news briefing podcast. Your tone should be authoritative yet conversational, 
suitable for audio consumption. Keep language clear and easy to follow when spoken aloud.
Use natural transitions between stories and maintain an engaging pace throughout.
""".strip()

# ---------------------------------------------------------------------------
# Anchor Script Instructions Template
# ---------------------------------------------------------------------------
ANCHOR_SCRIPT_INSTRUCTIONS = """
Create a cohesive anchor script for a news briefing podcast using ONLY the provided story summaries.

Input:
Date: {date}
Number of stories: {story_count}

Story Summaries:
{summaries}

Requirements:
1. Start with a brief, welcoming introduction mentioning the date and number of stories
2. Smoothly transition between each story using natural connective phrases
3. Present each summary in a conversational, audio-friendly manner
4. End with a concise closing statement
5. Total script should be approximately 3-5 minutes when read aloud
6. DO NOT add any information not present in the provided summaries
7. Maintain objectivity and professional news standards

Return ONLY the complete anchor script text, ready to be read aloud.
""".strip()
