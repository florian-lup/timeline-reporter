"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, researches, verifies,
                   # prioritizes, writes, and stores
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
    verify_leads,
    write_stories,
)
from utils import logger  # noqa: F401 – configure logging first


def run_pipeline() -> None:  # noqa: D401
    """Run the 7-step AI reporter pipeline."""
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

    # 3️⃣ Research (enhance leads with context and sources)
    researched_leads = research_lead(unique_leads, perplexity_client=perplexity_client)

    # 4️⃣ Verification (check lead credibility)
    verified_leads = verify_leads(researched_leads, openai_client=openai_client)

    # 5️⃣ Decision (prioritize most impactful leads based on research context)
    prioritized_leads = curate_leads(verified_leads, openai_client=openai_client)

    # 6️⃣ Writing (create stories from researched leads)
    stories = write_stories(prioritized_leads, openai_client=openai_client)

    # 7️⃣ Storage
    persist_stories(stories, mongodb_client=mongodb_client)

    logger.info(
        "Pipeline complete: %d stories stored",
        len(stories),
    )


if __name__ == "__main__":
    run_pipeline()
