from __future__ import annotations

from clients import OpenAIClient
from models import Lead
from utils import logger

from .hybrid_curator import HybridLeadCurator

# Log Preview Length
CONTEXT_PREVIEW_LENGTH = 50


def curate_leads(leads: list[Lead], *, openai_client: OpenAIClient) -> list[Lead]:
    """Selects the most impactful leads from deduplicated list.

    Uses hybrid AI evaluation combining multi-criteria scoring, pairwise comparison,
    and topic diversity to select only the top priority stories that warrant
    comprehensive research.
    """
    if not leads:
        logger.info("No leads to evaluate")
        return []

    logger.info("Evaluating %d leads for priority", len(leads))

    # Use the hybrid curation system
    curator = HybridLeadCurator(openai_client)
    selected_leads = curator.curate_leads(leads)

    logger.info("Selected %d priority leads", len(selected_leads))

    # Log the selected leads for transparency
    for i, lead in enumerate(selected_leads, 1):
        context_preview = (
            lead.context[:CONTEXT_PREVIEW_LENGTH] + "..."
            if len(lead.context) > CONTEXT_PREVIEW_LENGTH
            else lead.context
        )
        logger.info("Priority %d: %s", i, context_preview)

    return selected_leads
