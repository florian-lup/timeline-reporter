from __future__ import annotations

import json

from clients import PerplexityClient
from config.research_config import RESEARCH_INSTRUCTIONS
from models import Lead
from utils import logger

def research_lead(leads: list[Lead], *, perplexity_client: PerplexityClient) -> list[Lead]:
    """Research leads directly using Perplexity, similar to how discovery works."""
    enhanced_leads: list[Lead] = []

    for idx, lead in enumerate(leads, 1):
        first_words = " ".join(lead.title.split()[:5]) + "..."
        logger.info("  📚 Researching lead %d/%d - %s", idx, len(leads), first_words)

        # Use Perplexity to research the lead directly
        prompt = RESEARCH_INSTRUCTIONS.format(lead_title=lead.title)
        response_text = perplexity_client.lead_research(prompt)
        enhanced_lead = _enhance_lead_from_response(lead, response_text)
        enhanced_leads.append(enhanced_lead)
        source_count = len(enhanced_lead.sources) if enhanced_lead.sources else 0
        report_length = len(enhanced_lead.report.split()) if enhanced_lead.report else 0
        logger.info("  ✓ Research complete for lead %d/%d - %s", idx, len(leads), first_words)
        logger.info("  📊 Sources found: %d", source_count)
        logger.info("  📊 Report length: %d words", report_length)
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

    # Extract research results from response
    research_sources = data.get("sources") or []
    research_report = data.get("report") or ""

    # Create enhanced Lead with research results
    return Lead(
        title=original_lead.title,
        report=research_report,
        sources=research_sources,
        date=original_lead.date,
    )
