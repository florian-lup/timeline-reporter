from __future__ import annotations

import json
import re

from clients import PerplexityClient
from config import RESEARCH_INSTRUCTIONS
from models import Lead, Story
from utils import logger
from utils.date import get_today_formatted


def research_story(
    leads: list[Lead], *, perplexity_client: PerplexityClient
) -> list[Story]:
    """Calls Perplexity once per lead to generate full stories."""
    stories: list[Story] = []

    for lead in leads:
        prompt = RESEARCH_INSTRUCTIONS.format(
            lead_summary=lead.context, lead_date=lead.date
        )
        response_text = perplexity_client.lead_research(prompt)
        story = _parse_story_from_response(response_text)
        stories.append(story)

    logger.info("Generated %d stories", len(stories))
    return stories


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_story_from_response(response_text: str) -> Story:
    """Parse JSON from Perplexity and return a Story object."""
    # Some models wrap JSON in markdown triple-backticks; strip them if needed.
    fence_regex = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)
    match = fence_regex.search(response_text)
    json_blob = match.group(1) if match else response_text

    try:
        data = json.loads(json_blob)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("JSON parse failed: %s", exc)
        # Return a minimal Story with empty content
        return Story(
            headline="",
            summary="",
            body="",
            sources=[],
        )

    # Create Story from the JSON data, with fallbacks for missing fields and null values
    return Story(
        headline=data.get("headline") or "",
        summary=data.get("summary") or "",
        body=data.get("body") or "",
        sources=data.get("sources") or [],
        date=data.get("date") or get_today_formatted(),  # Use date from JSON or default
    )
