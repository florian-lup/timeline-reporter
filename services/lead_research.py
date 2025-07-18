from __future__ import annotations

import json

from clients import PerplexityClient
from config.research_config import RESEARCH_INSTRUCTIONS
from models import Lead, Story
from utils import logger
from utils.date import get_today_formatted


def research_lead(
    leads: list[Lead], *, perplexity_client: PerplexityClient
) -> list[Story]:
    """Calls Perplexity once per lead to generate full stories."""
    stories: list[Story] = []

    for lead in leads:
        prompt = RESEARCH_INSTRUCTIONS.format(
            lead_summary=lead.tip, lead_date=lead.date
        )
        response_text = perplexity_client.lead_research(prompt)
        story = _parse_lead_from_response(response_text)
        stories.append(story)

    logger.info("Generated %d stories", len(stories))
    return stories


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_lead_from_response(response_text: str) -> Story:
    """Parse JSON from Perplexity and return a Story object.

    The Perplexity client uses structured output and returns clean JSON.
    """
    try:
        data = json.loads(response_text)
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
