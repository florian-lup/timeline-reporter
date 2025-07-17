from __future__ import annotations

import json

from clients import PerplexityClient
from config import DISCOVERY_INSTRUCTIONS
from models import Lead
from utils import logger

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
    """Extracts JSON from the model response and maps to Lead objects.

    The Perplexity client uses structured output and returns clean JSON.
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("JSON parse failed: %s", exc)
        return []

    # Handle case where data might not be a list
    if not isinstance(data, list):
        logger.warning("Expected JSON array, got %s", type(data))
        return []

    leads: list[Lead] = [Lead(tip=item["tip"]) for item in data]
    return leads
