"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, prioritizes, researches,
                   # writes, and stores
"""

from __future__ import annotations

from clients import (
    MongoDBClient,
    OpenAIClient,
    PerplexityClient,
    PineconeClient,
)
from services import (
    curate_leads,
    deduplicate_leads,
    discover_leads,
    persist_stories,
    research_lead,
    write_stories,
)
from utils import logger  # noqa: F401 – configure logging first


def run_pipeline() -> None:  # noqa: D401
    """Run the 6-step AI reporter pipeline."""
    logger.info("Starting pipeline")

    # Initialise clients
    openai_client = OpenAIClient()
    pinecone_client = PineconeClient()
    perplexity_client = PerplexityClient()
    mongodb_client = MongoDBClient()

    # 1️⃣ Discovery
    leads = discover_leads(perplexity_client)

    # 2️⃣ Deduplication
    unique_leads = deduplicate_leads(
        leads, openai_client=openai_client, pinecone_client=pinecone_client
    )

    # 3️⃣ Decision (prioritize most impactful leads)
    prioritized_leads = curate_leads(unique_leads, openai_client=openai_client)

    # 4️⃣ Research (enhance leads with context and sources)
    researched_leads = research_lead(
        prioritized_leads, perplexity_client=perplexity_client
    )

    # 5️⃣ Writing (create stories from researched leads)
    stories = write_stories(researched_leads, openai_client=openai_client)

    # 6️⃣ Storage
    persist_stories(stories, mongodb_client=mongodb_client)

    logger.info(
        "Pipeline complete: %d stories stored",
        len(stories),
    )


if __name__ == "__main__":
    run_pipeline()
