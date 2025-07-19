from __future__ import annotations

import json

from clients import PerplexityClient
from config.discovery_config import (
    DISCOVERY_CATEGORIES,
    DISCOVERY_CATEGORY_INSTRUCTIONS,
)
from models import Lead
from utils import logger

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def discover_leads(perplexity_client: PerplexityClient) -> list[Lead]:
    """Discovers events for multiple topics using separate API calls for each category.

    Makes three API calls for:
    1. Politics, geopolitics, governments
    2. Environment, climate, natural disasters
    3. Celebrities, entertainment, sports

    Returns the combined list of events from all categories.
    """
    all_leads = []

    # Use centralized category configuration
    for category_name in DISCOVERY_CATEGORIES:
        logger.info("  📰 Scanning %s sources...", category_name)

        try:
            instructions = DISCOVERY_CATEGORY_INSTRUCTIONS[category_name]
            response_text = perplexity_client.lead_discovery(instructions)
            category_leads = _parse_leads_from_response(response_text)

            logger.info(
                "  ✓ %s: %d leads found",
                category_name.capitalize(),
                len(category_leads),
            )

            # Log each individual lead with first 5 words for tracking
            for idx, lead in enumerate(category_leads, 1):
                first_words = " ".join(lead.tip.split()[:5]) + "..."
                logger.info(
                    "    📋 Lead %d/%d - %s", idx, len(category_leads), first_words
                )

            all_leads.extend(category_leads)

        except Exception as exc:
            logger.error(
                "  ✗ %s: Discovery failed - %s", category_name.capitalize(), exc
            )
            # Continue with other categories even if one fails
            continue
    return all_leads


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
