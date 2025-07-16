from __future__ import annotations

from clients import OpenAIClient, PineconeClient
from models import Lead
from utils import logger

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
                lead.context[:50] + "..." if len(lead.context) > 50 else lead.context,
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
