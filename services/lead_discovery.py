from __future__ import annotations

import json

from clients import PerplexityClient
from config import (
    DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
    DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    DISCOVERY_POLITICS_INSTRUCTIONS,
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
    
    # Define categories with their respective instructions
    categories = [
        ("politics", DISCOVERY_POLITICS_INSTRUCTIONS),
        ("environment", DISCOVERY_ENVIRONMENT_INSTRUCTIONS),
        ("entertainment", DISCOVERY_ENTERTAINMENT_INSTRUCTIONS),
    ]
    
    # Make separate API calls for each category
    for category_name, instructions in categories:
        logger.info("Discovering leads for category: %s", category_name)
        
        try:
            response_text = perplexity_client.lead_discovery(instructions)
            category_leads = _parse_leads_from_response(response_text)
            
            logger.info("Discovered %d leads for %s", len(category_leads), category_name)
            all_leads.extend(category_leads)
            
        except Exception as exc:
            logger.error("Failed to discover leads for %s: %s", category_name, exc)
            # Continue with other categories even if one fails
            continue

    logger.info("Total leads discovered across all categories: %d", len(all_leads))
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
