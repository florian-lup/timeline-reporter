"""Service for identifying and removing duplicate leads using vector similarity."""

import logging

from clients.openai_client import OpenAIClient
from clients.pinecone_client import PineconeClient
from models.core import Lead

logger = logging.getLogger(__name__)

# Constants

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
        # Create embedding from the tip
        vector = openai_client.embed_text(lead.tip)

        # Query for similar existing leads
        matches = pinecone_client.similarity_search(vector)
        if matches:
            continue

        # Otherwise, upsert and keep
        vector_id = f"lead-{idx}"
        pinecone_client.upsert_vector(
            vector_id,
            vector,
            metadata={
                "tip": lead.tip,
                "date": lead.date,
            },
        )
        unique_leads.append(lead)

    logger.info("Deduplication complete: %d unique leads", len(unique_leads))
    return unique_leads
