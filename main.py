"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, prioritizes, researches, creates TTS broadcasts and stores articles
"""
from __future__ import annotations

from utils import logger  # noqa: F401 – configure logging first

from clients import MongoDBClient, OpenAIClient, PerplexityClient, PineconeClient
from services import (
    deduplicate_events,
    decide_events,
    discover_events,
    research_events,
    generate_broadcast_analysis,
    store_articles,
)


def run_pipeline() -> None:  # noqa: D401
    """Run the 6-step AI reporter pipeline."""

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
    prioritized_events = decide_events(unique_events, openai_client=openai_client)

    # 4️⃣ Research
    articles = research_events(prioritized_events, perplexity_client=perplexity_client)

    # 5️⃣ TTS Analysis & Broadcast Generation
    articles_with_broadcast = generate_broadcast_analysis(
        articles, openai_client=openai_client, mongodb_client=mongodb_client
    )

    # 6️⃣ Storage (now handled within TTS service, but keeping for consistency)
    # Note: Articles are already stored in MongoDB by the TTS service
    logger.info("Pipeline complete: %d articles with broadcasts", len(articles_with_broadcast))


if __name__ == "__main__":
    run_pipeline()
