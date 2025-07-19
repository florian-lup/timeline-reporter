from __future__ import annotations

from clients import MongoDBClient
from models import Story
from utils import logger

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def persist_stories(stories: list[Story], *, mongodb_client: MongoDBClient) -> None:
    """Stores stories in MongoDB."""
    for idx, story in enumerate(stories, 1):
        # Get first 5 words from the story's original lead tip
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
