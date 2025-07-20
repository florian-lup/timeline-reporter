"""MongoDB helper client using `pymongo`."""

from __future__ import annotations

from typing import Any

from pymongo import MongoClient

from config import MONGODB_COLLECTION_NAME, MONGODB_DATABASE_NAME, MONGODB_URI, MONGODB_COLLECTION_NAME_AUDIO
from utils import logger


class MongoDBClient:
    """Wrapper around `pymongo.MongoClient` scoped to the project database."""

    def __init__(self, uri: str | None = None):
        """Initialize MongoDB client.

        Args:
            uri: MongoDB connection URI. If None, uses MONGODB_URI from config.

        Raises:
            ValueError: If no URI is provided and MONGODB_URI is not set.
        """
        if uri is None:
            uri = MONGODB_URI
        if not uri:
            raise ValueError("MONGODB_URI is missing, cannot initialise MongoDB client.")
        if not MONGODB_DATABASE_NAME:
            raise ValueError("MONGODB_DATABASE_NAME is missing, cannot initialise MongoDB client.")
        if not MONGODB_COLLECTION_NAME:
            raise ValueError("MONGODB_COLLECTION_NAME is missing, cannot initialise MongoDB client.")
        self._client: MongoClient[dict[str, Any]] = MongoClient(uri)
        self._db = self._client[MONGODB_DATABASE_NAME]
        self._collection = self._db[MONGODB_COLLECTION_NAME]
        self._audio_collection = self._db[MONGODB_COLLECTION_NAME_AUDIO] if MONGODB_COLLECTION_NAME_AUDIO else None
        logger.info(
            "  ✓ MongoDB connected: %s/%s",
            MONGODB_DATABASE_NAME,
            MONGODB_COLLECTION_NAME,
        )
        if self._audio_collection is not None:
            logger.info(
                "  ✓ MongoDB audio collection ready: %s/%s",
                MONGODB_DATABASE_NAME,
                MONGODB_COLLECTION_NAME_AUDIO,
            )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def insert_story(self, story: dict[str, Any]) -> str:
        """Inserts *story* dict and returns inserted document id as str."""
        result = self._collection.insert_one(story)
        return str(result.inserted_id)

    def insert_podcast(self, podcast: dict[str, Any]) -> str:
        """Inserts *podcast* dict into audio collection and returns inserted document id as str."""
        if self._audio_collection is None:
            raise ValueError("Audio collection not configured. Set MONGODB_COLLECTION_NAME_AUDIO in environment.")
        result = self._audio_collection.insert_one(podcast)
        return str(result.inserted_id)
