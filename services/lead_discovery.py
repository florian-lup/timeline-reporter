from __future__ import annotations

import json
import re

from clients import PerplexityClient
from config import DISCOVERY_INSTRUCTIONS
from models import Lead
from utils import logger

# Older versions of the model sometimes wrap JSON in markdown fences; we keep a
# fallback regex but expect pure JSON due to `response_format=json_object`.
_FENCE_REGEX = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def discover_leads(perplexity_client: PerplexityClient) -> list[Lead]:
    """Discovers events for multiple topics in a single API call.

    Returns the combined list of events.
    """
    response_text = perplexity_client.lead_discovery(DISCOVERY_INSTRUCTIONS)
    leads = _parse_leads_from_response(response_text)

    logger.info("Discovered %d leads", len(leads))
    return leads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_leads_from_response(response_text: str) -> list[Lead]:
    """Extracts JSON from the model response and maps to Lead objects."""
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

    leads: list[Lead] = [Lead(context=item["context"]) for item in data]
    return leads
