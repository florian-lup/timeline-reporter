"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, researches, creates TTS broadcasts and stores articles
"""
from __future__ import annotations

from utils import logger  # noqa: F401 – configure logging first

from clients.mongodb import MongoDBClient
from clients.openai import OpenAIClient
from clients.perplexity import PerplexityClient
from clients.pinecone import PineconeClient
from services import (
    deduplicate_events,
    discover_events,
    research_events,
    generate_broadcast_analysis,
    store_articles,
)


def run_pipeline() -> None:  # noqa: D401
    """Run the 5-step AI reporter pipeline."""

    logger.info("Starting pipeline…")

    # Initialise clients
    openai_client = OpenAIClient()
    pinecone_client = PineconeClient()
    perplexity_client = PerplexityClient()
    mongodb_client = MongoDBClient()

    # 1️⃣ Discovery
    events = discover_events(openai_client)

    # 2️⃣ Deduplication
    unique_events = deduplicate_events(
        events, openai_client=openai_client, pinecone_client=pinecone_client
    )

    # 3️⃣ Research
    articles = research_events(unique_events, perplexity_client=perplexity_client)

    # 4️⃣ TTS Analysis & Broadcast Generation
    articles_with_broadcast = generate_broadcast_analysis(
        articles, openai_client=openai_client, mongodb_client=mongodb_client
    )

    # 5️⃣ Storage (now handled within TTS service, but keeping for consistency)
    # Note: Articles are already stored in MongoDB by the TTS service
    logger.info("Pipeline completed – %d articles processed with broadcasts.", len(articles_with_broadcast))


if __name__ == "__main__":
    run_pipeline()
