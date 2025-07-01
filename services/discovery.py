from __future__ import annotations

import json
import re
from typing import List

from clients.openai import OpenAIClient
from config.prompts import DISCOVERY_INSTRUCTIONS
from utils import logger, Event, get_today_formatted

# Older versions of the model sometimes wrap JSON in markdown fences; we keep a
# fallback regex but expect pure JSON due to `response_format=json_object`.
_FENCE_REGEX = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def discover_events(openai_client: OpenAIClient) -> List[Event]:
    """Discovers events for multiple topics in a single API call and returns the combined list."""

    topics = "climate, environment and natural disasters, and major geopolitical events"
    
    today = get_today_formatted()
    prompt = DISCOVERY_INSTRUCTIONS.format(topics=topics, date=today)
    response_text = openai_client.deep_research(prompt)
    logger.debug("Discovery response for combined topics: %s", response_text)
    events = _parse_events_from_response(response_text)

    logger.info("Discovered %d events from combined topics.", len(events))
    return events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_events_from_response(response_text: str) -> List[Event]:
    """Extracts JSON from the model response and maps to Event objects."""
    # Some models wrap JSON in markdown triple-backticks; strip them if needed.
    match = _FENCE_REGEX.search(response_text)
    json_blob = match.group(1) if match else response_text

    try:
        data = json.loads(json_blob)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("Failed to parse JSON, returning empty list. Error: %s", exc)
        return []

    # We no longer request or store source links at the discovery stage.
    events: list[Event] = [Event(title=item["title"], summary=item["summary"]) for item in data]
    return events










