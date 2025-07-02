"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, prioritizes, researches, creates TTS broadcasts and stores articles
"""
from __future__ import annotations

from utils import logger  # noqa: F401 – configure logging first

from clients import MongoDBClient, OpenAIClient, PerplexityClient, PineconeClient
from services import (
    deduplicate_events,
    select_events,
    discover_events,
    research_articles,
    generate_audio,
    insert_articles,
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
    prioritized_events = select_events(unique_events, openai_client=openai_client)

    # 4️⃣ Research
    articles = research_articles(prioritized_events, perplexity_client=perplexity_client)

    # 5️⃣ TTS Analysis & Broadcast Generation
    articles_with_broadcast = generate_audio(
        articles, openai_client=openai_client
    )

    # 6️⃣ Storage
    insert_articles(articles_with_broadcast, mongodb_client=mongodb_client)

    logger.info("Pipeline complete: %d articles with broadcasts stored", len(articles_with_broadcast))


if __name__ == "__main__":
    run_pipeline()
