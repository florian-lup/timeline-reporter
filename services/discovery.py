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

    response_text = perplexity_client.deep_research(DISCOVERY_INSTRUCTIONS)
    events = _parse_events_from_response(response_text)

    logger.info("Discovered %d events", len(events))
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
        logger.warning("JSON parse failed: %s", exc)
        return []

    # Handle case where data might not be a list
    if not isinstance(data, list):
        logger.warning("Expected JSON array, got %s", type(data))
        return []

    # We no longer request or store source links at the discovery stage.
    events: list[Event] = [Event(title=item["title"], summary=item["summary"]) for item in data]
    return events










