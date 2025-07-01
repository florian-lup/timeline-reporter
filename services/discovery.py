from __future__ import annotations

import json
import re
from typing import List

from clients import PerplexityClient
from config import DISCOVERY_INSTRUCTIONS
from utils import logger, Event

# Older versions of the model sometimes wrap JSON in markdown fences; we keep a
# fallback regex but expect pure JSON due to `response_format=json_object`.
_FENCE_REGEX = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def discover_events(perplexity_client: PerplexityClient) -> List[Event]:
    """Discovers events for multiple topics in a single API call and returns the combined list."""

    logger.info("Sending prompt to Perplexity: %s", DISCOVERY_INSTRUCTIONS)
    response_text = perplexity_client.deep_research(DISCOVERY_INSTRUCTIONS)
    logger.info("RAW Discovery response for combined topics: %s", response_text)
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
    
    logger.info("JSON blob to parse: %s", json_blob[:500] + "..." if len(json_blob) > 500 else json_blob)

    try:
        data = json.loads(json_blob)
        logger.info("Successfully parsed JSON. Type: %s, Length: %s", type(data), len(data) if isinstance(data, (list, dict)) else "N/A")
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.error("Failed to parse JSON, returning empty list. Error: %s", exc)
        logger.error("Raw response text was: %s", response_text[:1000] + "..." if len(response_text) > 1000 else response_text)
        return []

    # Handle case where data might not be a list
    if not isinstance(data, list):
        logger.error("Expected JSON array but got %s: %s", type(data), data)
        return []

    # We no longer request or store source links at the discovery stage.
    events: list[Event] = [Event(title=item["title"], summary=item["summary"]) for item in data]
    return events










