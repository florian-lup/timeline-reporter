from __future__ import annotations

from typing import List

from clients import OpenAIClient, PineconeClient
from utils import logger, Event


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def deduplicate_events(
    events: List[Event],
    *,
    openai_client: OpenAIClient,
    pinecone_client: PineconeClient,
) -> List[Event]:
    """Removes near-duplicate events based on vector similarity.

    Each *event*'s summary is embedded and compared against existing vectors in
    Pinecone. Anything with a similarity ≥ threshold is dropped.
    """

    unique_events: list[Event] = []

    for idx, event in enumerate(events):
        # Create embedding
        text_for_embedding = event.title + "\n" + event.summary
        vector = openai_client.embed_text(text_for_embedding)

        # Query for similar existing events
        matches = pinecone_client.similarity_search(vector)
        if matches:
            logger.info(
                "Skipping duplicate event '%s' (matched %d existing with score %.2f)",
                event.title,
                len(matches),
                matches[0][1],
            )
            continue

        # Otherwise, upsert and keep
        vector_id = f"event-{idx}"
        pinecone_client.upsert_vector(
            vector_id,
            vector,
            metadata={"title": event.title, "summary": event.summary},
        )
        unique_events.append(event)

    logger.info("%d unique events after deduplication.", len(unique_events))
    return unique_events 