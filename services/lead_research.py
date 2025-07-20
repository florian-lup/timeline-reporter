from __future__ import annotations

import json

from clients import PerplexityClient
from config.research_config import RESEARCH_INSTRUCTIONS
from models import Lead
from utils import combine_and_deduplicate_sources, logger

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
    Combines existing sources from discovery with new sources from research.
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("JSON parse failed: %s", exc)
        # Return the original lead unchanged
        return original_lead

    # Get new sources from research
    new_sources = data.get("sources") or []
    
    # Combine existing sources from discovery with new research sources
    # Use URL-aware deduplication to catch similar URLs
    combined_sources = combine_and_deduplicate_sources(original_lead.sources, new_sources)

    # Append research findings to existing discovery report
    research_report = data.get("report") or ""
    if original_lead.report and research_report:
        # Both discovery and research have content - combine them
        combined_report = f"{original_lead.report}\n\n{research_report}"
    elif research_report:
        # Only research has content
        combined_report = research_report
    else:
        # Keep original report (discovery only or empty)
        combined_report = original_lead.report

    # Create enhanced Lead with combined report and sources
    return Lead(
        title=original_lead.title,
        report=combined_report,
        sources=combined_sources,
        date=original_lead.date,
    )
