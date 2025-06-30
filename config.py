"""Centralised configuration settings for the project."""

from __future__ import annotations

import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from `.env`
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# ---------------------------------------------------------------------------
# Pinecone
# ---------------------------------------------------------------------------
PINECONE_INDEX_NAME: str = "timeline-events"
SIMILARITY_THRESHOLD: float = 0.8
TOP_K_RESULTS: int = 5

# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
DEEP_RESEARCH_MODEL: str = "o4-mini-deep-research"
EMBEDDING_MODEL: str = "text-embedding-3-small"
EMBEDDING_DIMENSIONS: int = 1536

# ---------------------------------------------------------------------------
# Perplexity
# ---------------------------------------------------------------------------
RESEARCH_MODEL: str = "sonar"
SEARCH_CONTEXT_SIZE: str = "medium"

# ---------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------
MONGODB_DATABASE_NAME: str = "events"
MONGODB_COLLECTION_NAME: str = "articles"