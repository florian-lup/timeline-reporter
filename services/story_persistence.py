from __future__ import annotations

from clients import MongoDBClient
from models import Podcast, Story
from utils import logger

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def persist_stories(stories: list[Story], *, mongodb_client: MongoDBClient) -> None:
    """Stores stories in MongoDB."""
    for idx, story in enumerate(stories, 1):
        # Get first 5 words from the story's original discovered lead
        # (stored in metadata if available)
        # For now, use story headline as fallback
        first_words = " ".join(story.headline.split()[:5]) + "..."
        logger.info("  💾 Saving story %d/%d - %s", idx, len(stories), first_words)
        story_dict = story.__dict__.copy()
        inserted_id = mongodb_client.insert_story(story_dict)
        logger.info(
            "  ✓ Story %d/%d saved successfully - %s (ID: %s)",
            idx,
            len(stories),
            first_words,
            inserted_id[:12] + "...",
        )


def persist_podcast(podcast: Podcast, *, mongodb_client: MongoDBClient) -> str:
    """Stores podcast metadata in MongoDB.

    Args:
        podcast: Podcast object to persist
        mongodb_client: MongoDB client for database operations

    Returns:
        MongoDB document ID of the stored podcast
    """
    logger.info("🎙️ STEP 7: Persistence - Saving podcast metadata to database...")
    logger.info("  💾 Saving podcast metadata...")
    podcast_dict = podcast.__dict__.copy()
    inserted_id = mongodb_client.insert_podcast(podcast_dict)
    logger.info("  ✓ Podcast saved with CDN URL (ID: %s)", inserted_id[:12] + "...")

    logger.info("✅ Persistence complete: podcast metadata stored")
    return inserted_id


def persist_stories_and_podcast(
    stories: list[Story],
    podcast: Podcast,
    *,
    mongodb_client: MongoDBClient,
) -> str:
    """Stores both stories and podcast metadata in MongoDB.

    Args:
        stories: List of Story objects to persist
        podcast: Podcast object to persist
        mongodb_client: MongoDB client for database operations

    Returns:
        MongoDB document ID of the stored podcast
    """
    logger.info("🎙️ STEP 7: Persistence - Saving stories and podcast metadata...")

    # Persist stories first
    logger.info("  📰 Persisting %d stories...", len(stories))
    persist_stories(stories, mongodb_client=mongodb_client)

    # Then persist podcast
    logger.info("  🎙️ Persisting podcast metadata...")
    podcast_dict = podcast.__dict__.copy()
    inserted_id = mongodb_client.insert_podcast(podcast_dict)
    logger.info("  ✓ Podcast saved with CDN URL (ID: %s)", inserted_id[:12] + "...")

    logger.info("✅ Persistence complete: %d stories and podcast saved", len(stories))
    return inserted_id
