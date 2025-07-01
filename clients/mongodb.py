"""MongoDB helper client using `pymongo`."""
from __future__ import annotations

from pymongo import MongoClient

from config import MONGODB_COLLECTION_NAME, MONGODB_DATABASE_NAME, MONGODB_URI
from utils import logger


class MongoDBClient:
    """Wrapper around `pymongo.MongoClient` scoped to the project database."""

    def __init__(self, uri: str | None = None):
        if uri is None:
            uri = MONGODB_URI
        if not uri:
            raise ValueError("MONGODB_URI is missing, cannot initialise MongoDB client.")
        self._client = MongoClient(uri)
        self._db = self._client[MONGODB_DATABASE_NAME]
        self._collection = self._db[MONGODB_COLLECTION_NAME]
        logger.info("Connected to MongoDB database=%s collection=%s", MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def insert_article(self, article: dict) -> str:
        """Inserts *article* dict and returns inserted document id as str."""
        logger.debug("Inserting article: %s", article.get("headline"))
        result = self._collection.insert_one(article)
        return str(result.inserted_id)
