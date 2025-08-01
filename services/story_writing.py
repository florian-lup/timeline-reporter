from __future__ import annotations

import json

from clients import OpenAIClient
from config.writing_config import (
    STORY_WRITING_SCHEMA,
    WRITING_INSTRUCTIONS,
    WRITING_MODEL,
    WRITING_SYSTEM_PROMPT,
)
from models import Lead, Story
from utils import logger

# Constants for magic values
MAX_HEADLINE_DISPLAY_LENGTH = 60


def write_stories(leads: list[Lead], *, openai_client: OpenAIClient) -> list[Story]:
    """Takes researched leads and writes full stories using GPT-4o."""
    stories: list[Story] = []

    for idx, lead in enumerate(leads, 1):
        first_words = " ".join(lead.discovered_lead.split()[:5]) + "..."
        logger.info("  ✍️ Writing story %d/%d - %s", idx, len(leads), first_words)

        # Format the writing prompt with report and date
        user_prompt = WRITING_INSTRUCTIONS.format(
            lead_date=lead.date,
            lead_report=lead.report,
        )

        # Generate the story using GPT-4o with structured output
        response_text = openai_client.chat_completion(
            user_prompt,
            model=WRITING_MODEL,
            system_prompt=WRITING_SYSTEM_PROMPT,
            response_format={"type": "json_schema", "json_schema": STORY_WRITING_SCHEMA},
        )

        story = _parse_story_from_response(response_text, lead)
        stories.append(story)
        headline_display = story.headline[:MAX_HEADLINE_DISPLAY_LENGTH] + ("..." if len(story.headline) > MAX_HEADLINE_DISPLAY_LENGTH else "")
        logger.info(
            "  ✓ Story %d/%d completed - %s: '%s'",
            idx,
            len(leads),
            first_words,
            headline_display,
        )
    return stories


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_story_from_response(response_text: str, lead: Lead) -> Story:
    """Parse the GPT-4o JSON response and create a Story object."""
    try:
        data = json.loads(response_text)

        return Story(
            headline=data.get("headline", "").strip(),
            summary=data.get("summary", "").strip(),
            body=data.get("body", "").strip(),
            tag=data.get("tag", "other").strip(),
            sources=lead.sources,
            date=lead.date,
        )

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse JSON response: %s", exc)
        logger.debug("Response was: %s", response_text[:500])
        raise
