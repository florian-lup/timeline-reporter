from __future__ import annotations

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
        content, citations = perplexity_client.lead_research(prompt)
        
        enhanced_lead = _enhance_lead_from_response(lead, content, citations)
        enhanced_leads.append(enhanced_lead)
        citation_count = len(citations) if citations else 0
        report_length = len(enhanced_lead.report.split()) if enhanced_lead.report else 0
        logger.info("  ✓ Research complete for lead %d/%d - %s", idx, len(leads), first_words)
        logger.info("  📊 Citations found: %d", citation_count)
        logger.info("  📊 Report length: %d words", report_length)
    return enhanced_leads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _enhance_lead_from_response(original_lead: Lead, content: str, citations: list[str]) -> Lead:
    """Parse response from Perplexity and enhance the Lead object.
    
    Uses the content as the report and citations directly from Perplexity's response.
    """
    # Use the content as the report
    report = content.strip()
    
    # Use citations directly from Perplexity's response
    sources = citations or []
    
    # Create enhanced Lead with research results
    return Lead(
        title=original_lead.title,
        report=report,
        sources=sources,
        date=original_lead.date,
    )
