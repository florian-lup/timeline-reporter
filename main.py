"""Entry point for running the timeline-reporter pipeline.

Usage::

    python -m main  # discovers, deduplicates, researches,
                   # prioritizes, writes, and stores
"""

from __future__ import annotations

from clients import (
    CloudflareR2Client,
    MongoDBClient,
    OpenAIClient,
    PerplexityClient,
    PineconeClient,
)
from services import (
    curate_leads,
    deduplicate_leads,
    discover_leads,
    generate_podcast,
    persist_stories,
    research_lead,
    write_stories,
)
from utils import logger  # noqa: F401 – configure logging first


def run_pipeline() -> None:  # noqa: D401
    """Run the 6-step AI reporter pipeline."""
    logger.info("🚀 PIPELINE STARTED: Timeline Reporter")

    # Initialise clients
    logger.info("📡 SETUP: Initializing clients...")
    openai_client = OpenAIClient()
    pinecone_client = PineconeClient()
    perplexity_client = PerplexityClient()
    mongodb_client = MongoDBClient()
    r2_client = CloudflareR2Client()

    # 1️⃣ Discovery
    logger.info("🔍 STEP 1: Lead Discovery - Scanning news sources for breaking stories...")
    leads = discover_leads(perplexity_client)
    logger.info("✅ Discovery complete: Found %d leads across all categories", len(leads))

    # 2️⃣ Deduplication
    logger.info("🔄 STEP 2: Deduplication - Removing duplicate stories...")
    unique_leads = deduplicate_leads(leads, openai_client=openai_client, pinecone_client=pinecone_client)
    duplicates_removed = len(leads) - len(unique_leads)
    logger.info(
        "✅ Deduplication complete: %d duplicates removed, %d unique leads remain",
        duplicates_removed,
        len(unique_leads),
    )

    # 3️⃣ Research
    logger.info(
        "📚 STEP 3: Research - Gathering context and sources for %d leads...",
        len(unique_leads),
    )
    researched_leads = research_lead(unique_leads, perplexity_client=perplexity_client)
    logger.info(
        "✅ Research complete: Enhanced %d leads with detailed context",
        len(researched_leads),
    )

    # 4️⃣ Decision (prioritize most impactful leads based on research context)
    logger.info(
        "⚖️ STEP 4: Curation - Evaluating %d leads for impact and priority...",
        len(researched_leads),
    )
    prioritized_leads = curate_leads(researched_leads, openai_client=openai_client)
    logger.info(
        "✅ Curation complete: Selected %d high-priority leads for publication",
        len(prioritized_leads),
    )

    # 5️⃣ Writing (create stories from researched leads)
    logger.info(
        "✍️ STEP 5: Writing - Generating stories from %d priority leads...",
        len(prioritized_leads),
    )
    stories = write_stories(prioritized_leads, openai_client=openai_client)
    logger.info("✅ Writing complete: Generated %d publication-ready stories", len(stories))

    # 6️⃣ Storage
    logger.info("💾 STEP 6: Storage - Saving %d stories to database...", len(stories))
    persist_stories(stories, mongodb_client=mongodb_client)

    # 7️⃣ Audio Generation
    if stories:  # Only generate podcast if we have stories
        try:
            podcast = generate_podcast(stories, openai_client=openai_client, mongodb_client=mongodb_client, r2_client=r2_client)
            logger.info(
                "🎙️ Podcast generated: %d-story briefing",
                len(stories),
            )
        except Exception as e:
            logger.error("Failed to generate podcast: %s", str(e))
            # Continue pipeline even if audio generation fails

    logger.info(
        "🎉 PIPELINE COMPLETE: Successfully processed %d leads → %d stories published",
        len(leads),
        len(stories),
    )


if __name__ == "__main__":
    run_pipeline()
