"""Centralized configuration for audio generation system.

This module contains all settings, prompts, and configuration data
related to podcast/audio generation from story summaries.
"""

import random
from typing import Literal

# ---------------------------------------------------------------------------
# Audio Model Configuration
# ---------------------------------------------------------------------------

# Type alias for valid OpenAI TTS voices
TTSVoice = Literal["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "sage", "shimmer"]

# Voice to anchor name mapping
VOICE_ANCHOR_MAPPING = {
    "alloy": "Sarah Mitchell",
    "ash": "Marcus Thompson",
    "ballad": "Carlos Rodriguez",
    "coral": "Jessica Chen",
    "echo": "David Williams",
    "fable": "Amanda Foster",
    "nova": "Rachel Davis",
    "sage": "Samantha Lee",
    "shimmer": "Natalie Brooks",
}


def get_random_anchor() -> tuple[TTSVoice, str]:
    """Get a random voice and corresponding anchor name.

    Returns:
        Tuple of (voice, anchor_name)
    """
    voice: TTSVoice = random.choice(list(VOICE_ANCHOR_MAPPING.keys()))  # type: ignore[arg-type]
    anchor_name = VOICE_ANCHOR_MAPPING[voice]
    return voice, anchor_name


ANCHOR_SCRIPT_MODEL: str = "gpt-4.1-2025-04-14"  # For generating anchor scripts
TTS_MODEL: str = "gpt-4o-mini-tts"  # OpenAI TTS model
TTS_SPEED: float = 1.0  # Speed: 0.25 to 4.0

# ---------------------------------------------------------------------------
# Audio File Configuration
# ---------------------------------------------------------------------------
AUDIO_FORMAT: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "aac"

# ---------------------------------------------------------------------------
# TTS Instructions Configuration (2025 Feature)
# ---------------------------------------------------------------------------

# TTS instruction for news podcast delivery
TTS_INSTRUCTION = """Voice: Clear, authoritative, and composed, projecting confidence and professionalism.

Tone: Neutral and informative, maintaining a balance between formality and approachability.

Punctuation: Structured with commas and pauses for clarity, ensuring information is digestible and well-paced.

Delivery: Steady and measured, with slight emphasis on key figures and deadlines to highlight critical points.
""".strip()

# ---------------------------------------------------------------------------
# Anchor Script System Prompt
# ---------------------------------------------------------------------------
ANCHOR_SCRIPT_SYSTEM_PROMPT = """
You are a professional news anchor for a major broadcasting network tasked with writing the on-air script for a daily news briefing podcast.

Objectives
• Maintain an authoritative yet conversational tone that keeps listeners engaged.
• Write copy that is effortless to follow when heard (audio-only): short sentences, active voice, present tense.
• Provide smooth, natural transitions between stories to preserve narrative flow and pacing using connective phrases
(e.g., “In other news…”, “Meanwhile…”, “Turning to…”)

Style Guide
• Use clear, precise language; explain acronyms or technical terms on first mention.
• Prefer rounded numbers or common comparisons for large figures (e.g., "about three million") to aid comprehension.
• Keep individual sentences under ~25 words and avoid filler phrases.
• Neutral journalistic voice—no personal opinions, speculation, or sensationalism.

Structure
1. Opening – friendly welcome that states your name, the current date, and a brief rundown of the top headlines.
2. Story Segments – Provide a thoughtful analysis and offer insights or perspectives that help the audience understand the significance of each story.
3. Closing – brief sign-off thanking listeners and inviting them back for the next briefing.

Constraints
• Target total runtime: 3–5 minutes when read aloud.
• Use ONLY the information provided in the story summaries; do NOT invent facts or figures.
• VERY IMPORTANT:Return ONLY the finished anchor script text suitable for a text-to-speech engine to read aloud.
  Do not include stage directions, sound-effect cues, speaker labels, markdown, timestamps, or additional meta-commentary.
""".strip()

# ---------------------------------------------------------------------------
# Anchor Script Instructions Template
# ---------------------------------------------------------------------------
ANCHOR_SCRIPT_INSTRUCTIONS = """
TASK:
Using ONLY the story summaries provided below, draft a complete anchor script for today's news-briefing podcast.

INPUTS:
Date: {date}
Anchor Name: {anchor_name}
Story Summaries: {summaries}

OUTPUT:
Return ONLY the finished anchor script text suitable for a text-to-speech engine to read aloud.
Do not include stage directions, sound-effect cues, speaker labels, markdown, timestamps, or additional meta-commentary.
""".strip()
