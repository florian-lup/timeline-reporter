from __future__ import annotations

import json

from clients import PerplexityClient
from config.research_config import RESEARCH_INSTRUCTIONS
from models import Lead
from utils import logger


def research_lead(
    leads: list[Lead], *, perplexity_client: PerplexityClient
) -> list[Lead]:
    """Calls Perplexity once per lead to gather context and sources."""
    enhanced_leads: list[Lead] = []

    for lead in leads:
        prompt = RESEARCH_INSTRUCTIONS.format(lead_tip=lead.tip, lead_date=lead.date)
        response_text = perplexity_client.lead_research(prompt)
        enhanced_lead = _enhance_lead_from_response(lead, response_text)
        enhanced_leads.append(enhanced_lead)

    logger.info("Enhanced %d leads with research", len(enhanced_leads))
    return enhanced_leads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _enhance_lead_from_response(original_lead: Lead, response_text: str) -> Lead:
    """Parse JSON from Perplexity and enhance the Lead object.

    The Perplexity client uses structured output and returns clean JSON.
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("JSON parse failed: %s", exc)
        # Return the original lead unchanged
        return original_lead

    # Create enhanced Lead with context and sources from the JSON data
    return Lead(
        tip=original_lead.tip,
        context=data.get("context") or "",
        sources=data.get("sources") or [],
        date=original_lead.date,
    )
