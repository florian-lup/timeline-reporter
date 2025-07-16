from __future__ import annotations

from clients import OpenAIClient, PineconeClient
from models import Lead
from utils import logger

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def deduplicate_leads(
    events: list[Lead],
    *,
    openai_client: OpenAIClient,
    pinecone_client: PineconeClient,
) -> list[Lead]:
    """Removes near-duplicate events based on vector similarity.

    Each *event*'s context is embedded and compared against existing vectors in
    Pinecone. Anything with a similarity ≥ threshold is dropped.
    """
    unique_events: list[Lead] = []

    for idx, event in enumerate(events):
        # Create embedding from the context
        vector = openai_client.embed_text(event.context)

        # Query for similar existing events
        matches = pinecone_client.similarity_search(vector)
        if matches:
            logger.info(
                "Skipping duplicate: '%s' (similarity: %.2f)",
                event.context[:50] + "..." if len(event.context) > 50 else event.context,
                matches[0][1],
            )
            continue

        # Otherwise, upsert and keep
        vector_id = f"event-{idx}"
        pinecone_client.upsert_vector(
            vector_id,
            vector,
            metadata={
                "context": event.context,
                "date": event.date,
            },
        )
        unique_events.append(event)

    logger.info("Deduplication complete: %d unique events", len(unique_events))
    return unique_events
