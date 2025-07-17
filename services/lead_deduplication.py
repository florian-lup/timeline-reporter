"""Service for identifying and removing duplicate leads using vector similarity."""

import logging

from clients.openai_client import OpenAIClient
from clients.pinecone_client import PineconeClient
from models.core import Lead

logger = logging.getLogger(__name__)

# Constants
CONTEXT_PREVIEW_LENGTH = 50

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def deduplicate_leads(
    leads: list[Lead],
    *,
    openai_client: OpenAIClient,
    pinecone_client: PineconeClient,
) -> list[Lead]:
    """Removes near-duplicate leads based on vector similarity.

    Each *lead*'s context is embedded and compared against existing vectors in
    Pinecone. Anything with a similarity ≥ threshold is dropped.
    """
    unique_leads: list[Lead] = []

    for idx, lead in enumerate(leads):
        # Create embedding from the context
        vector = openai_client.embed_text(lead.context)

        # Query for similar existing leads
        matches = pinecone_client.similarity_search(vector)
        if matches:
            logger.info(
                "Skipping duplicate: '%s' (similarity: %.2f)",
                (
                    lead.context[:CONTEXT_PREVIEW_LENGTH] + "..."
                    if len(lead.context) > CONTEXT_PREVIEW_LENGTH
                    else lead.context
                ),
                matches[0][1],
            )
            continue

        # Otherwise, upsert and keep
        vector_id = f"lead-{idx}"
        pinecone_client.upsert_vector(
            vector_id,
            vector,
            metadata={
                "context": lead.context,
                "date": lead.date,
            },
        )
        unique_leads.append(lead)

    logger.info("Deduplication complete: %d unique leads", len(unique_leads))
    return unique_leads
