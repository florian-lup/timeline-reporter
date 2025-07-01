"""Wrapper around Pinecone client utilities."""
from __future__ import annotations

from typing import List

from pinecone import Pinecone, ServerlessSpec

from config import (
    CLOUD_PROVIDER,
    CLOUD_REGION,
    EMBEDDING_DIMENSIONS,
    METRIC,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
)
from utils import logger


class PineconeClient:
    """Encapsulates Pinecone connection and operations used in the pipeline."""

    def __init__(self, api_key: str | None = None, *, environment: str | None = None):
        if api_key is None:
            api_key = PINECONE_API_KEY
        if not api_key:
            raise ValueError("PINECONE_API_KEY is missing, cannot initialise Pinecone client.")

        logger.info("Initializing Pinecone")
        self._pc = Pinecone(api_key=api_key)
        self._index = self._ensure_index()
        logger.info("Pinecone ready: %s", PINECONE_INDEX_NAME)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def similarity_search(self, vector: List[float], *, top_k: int | None = None) -> List[tuple[str, float]]:
        """Returns list of (id, score) above SIMILARITY_THRESHOLD for *vector*."""
        if top_k is None:
            top_k = TOP_K_RESULTS
        res = self._index.query(vector=vector, top_k=top_k, include_values=False)
        return [
            (m.id, m.score) for m in res.matches if m.score and m.score >= SIMILARITY_THRESHOLD
        ]

    def upsert_vector(self, vector_id: str, values: List[float], metadata: dict | None = None) -> None:
        self._index.upsert([(vector_id, values, metadata or {})])

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _ensure_index(self):  # noqa: D401
        """Return an existing index or create if missing."""
        existing_indexes = self._pc.list_indexes().names()
        if PINECONE_INDEX_NAME not in existing_indexes:
            logger.info("Creating index: %s", PINECONE_INDEX_NAME)
            self._pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSIONS,
                metric=METRIC,
                spec=ServerlessSpec(
                    cloud=CLOUD_PROVIDER,
                    region=CLOUD_REGION
                ),
            )
        return self._pc.Index(PINECONE_INDEX_NAME)
