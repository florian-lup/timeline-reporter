"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, researches and stores articles
"""
from __future__ import annotations

from utils.logger import logger  # noqa: F401 – configure logging first

from clients.mongodb import MongoDBClient
from clients.openai import OpenAIClient
from clients.perplexity import PerplexityClient
from clients.pinecone import PineconeClient
from services.deduplication import deduplicate_events
from services.discovery import discover_events
from services.research import research_events
from services.storage import store_articles


def run_pipeline() -> None:  # noqa: D401
    """Run the 4-step AI reporter pipeline."""

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

    # 4️⃣ Storage
    store_articles(articles, mongodb_client=mongodb_client)

    logger.info("Pipeline completed – %d articles stored.", len(articles))


if __name__ == "__main__":
    run_pipeline()
