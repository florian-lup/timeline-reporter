from __future__ import annotations

import json

from clients import OpenAIClient
from config.writing_config import (
    JSON_FORMAT_INSTRUCTION,
    WRITING_INSTRUCTIONS,
    WRITING_MODEL,
    WRITING_SYSTEM_PROMPT,
    WRITING_TEMPERATURE,
)
from models import Lead, Story
from utils import logger


def write_stories(leads: list[Lead], *, openai_client: OpenAIClient) -> list[Story]:
    """Takes researched leads and writes full stories using GPT-4o."""
    stories: list[Story] = []

    for lead in leads:
        # Format the writing prompt with only context and date
        user_prompt = WRITING_INSTRUCTIONS.format(
            lead_date=lead.date,
            lead_context=lead.context,
        )

        # Combine system prompt, user prompt, and JSON format instruction
        full_prompt = (
            f"{WRITING_SYSTEM_PROMPT}\n\n{user_prompt}{JSON_FORMAT_INSTRUCTION}"
        )

        # Generate the story using GPT-4o with JSON response format
        response_text = openai_client.chat_completion(
            full_prompt,
            model=WRITING_MODEL,
            temperature=WRITING_TEMPERATURE,
            response_format={"type": "json_object"},
        )

        story = _parse_story_from_response(response_text, lead)
        stories.append(story)

    logger.info("Generated %d stories", len(stories))
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
            sources=lead.sources,
            date=lead.date,
        )

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse JSON response: %s", exc)
        logger.debug("Response was: %s", response_text[:500])
        raise
