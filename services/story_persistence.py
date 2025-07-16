from __future__ import annotations

from clients import MongoDBClient
from models import Story
from utils import logger

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def persist_stories(stories: list[Story], *, mongodb_client: MongoDBClient) -> None:
    """Stores stories in MongoDB."""
    for story in stories:
        story_dict = story.__dict__.copy()
        inserted_id = mongodb_client.insert_story(story_dict)
        logger.info("Stored story: '%s' (id=%s)", story.headline, inserted_id)
