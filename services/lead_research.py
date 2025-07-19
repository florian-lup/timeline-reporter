from __future__ import annotations

import json

from clients import OpenAIClient, PerplexityClient
from config.research_config import (
    QUERY_FORMULATION_INSTRUCTIONS,
    QUERY_FORMULATION_MODEL,
    RESEARCH_INSTRUCTIONS,
)
from models import Lead
from utils import logger

def research_lead(leads: list[Lead], *, openai_client: OpenAIClient, perplexity_client: PerplexityClient) -> list[Lead]:
    """Calls OpenAI to formulate search queries, then Perplexity to gather context and sources."""
    enhanced_leads: list[Lead] = []

    for idx, lead in enumerate(leads, 1):
        first_words = " ".join(lead.tip.split()[:5]) + "..."
        logger.info("  📚 Researching lead %d/%d - %s", idx, len(leads), first_words)

        # Step 1: Use OpenAI to formulate an effective search query
        logger.info("  🔍 Formulating search query for lead %d/%d", idx, len(leads))
        search_query = _formulate_search_query(lead, openai_client=openai_client)
        logger.info("  ✓ Query formulated: %s", search_query)

        # Step 2: Use Perplexity to research the formulated query
        prompt = RESEARCH_INSTRUCTIONS.format(search_query=search_query, lead_date=lead.date)
        response_text = perplexity_client.lead_research(prompt)
        enhanced_lead = _enhance_lead_from_response(lead, response_text)
        enhanced_leads.append(enhanced_lead)
        source_count = len(enhanced_lead.sources) if enhanced_lead.sources else 0
        logger.info("  ✓ Research complete for lead %d/%d - %s", idx, len(leads), first_words)
        logger.info("  📊 Sources found: %d", source_count)
    return enhanced_leads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _formulate_search_query(lead: Lead, *, openai_client: OpenAIClient) -> str:
    """Use OpenAI to transform the raw tip into an effective search query for Perplexity."""
    prompt = QUERY_FORMULATION_INSTRUCTIONS.format(lead_tip=lead.tip, lead_date=lead.date)

    try:
        search_query = openai_client.chat_completion(
            prompt=prompt,
            model=QUERY_FORMULATION_MODEL,
        )
        return search_query.strip()
    except Exception as exc:  # pragma: no cover
        logger.warning("Query formulation failed: %s. Using original tip.", exc)
        # Fallback to original tip if query formulation fails
        return lead.tip


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
    # Use a set to avoid duplicates, then convert back to list
    combined_sources = list(set(original_lead.sources + new_sources))

    # Create enhanced Lead with context and combined sources from the JSON data
    return Lead(
        tip=original_lead.tip,
        context=data.get("context") or "",
        sources=combined_sources,
        date=original_lead.date,
    )
