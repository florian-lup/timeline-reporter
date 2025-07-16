"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, prioritizes, researches, and stores articles
"""

from __future__ import annotations

from clients import MongoDBClient, OpenAIClient, PerplexityClient, PineconeClient
from services import (
    deduplicate_events,
    discover_events,
    insert_articles,
    research_articles,
    select_events,
)
from utils import logger  # noqa: F401 – configure logging first


def run_pipeline() -> None:  # noqa: D401
    """Run the 5-step AI reporter pipeline."""
    logger.info("Starting pipeline")

    # Initialise clients
    openai_client = OpenAIClient()
    pinecone_client = PineconeClient()
    perplexity_client = PerplexityClient()
    mongodb_client = MongoDBClient()

    # 1️⃣ Discovery
    events = discover_events(perplexity_client)

    # 2️⃣ Deduplication
    unique_events = deduplicate_events(
        events, openai_client=openai_client, pinecone_client=pinecone_client
    )

    # 3️⃣ Decision (new step: prioritize most impactful events)
    prioritized_events = select_events(unique_events, openai_client=openai_client)

    # 4️⃣ Research
    articles = research_articles(
        prioritized_events, perplexity_client=perplexity_client
    )

    # 5️⃣ Storage
    insert_articles(articles, mongodb_client=mongodb_client)

    logger.info(
        "Pipeline complete: %d articles stored",
        len(articles),
    )


if __name__ == "__main__":
    run_pipeline()
