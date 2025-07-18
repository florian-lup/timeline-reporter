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
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
CLOUD_PROVIDER = os.getenv("CLOUD_PROVIDER")
CLOUD_REGION = os.getenv("CLOUD_REGION")

# ---------------------------------------------------------------------------
# Pinecone
# ---------------------------------------------------------------------------
SIMILARITY_THRESHOLD: float = 0.8
TOP_K_RESULTS: int = 5

# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = "text-embedding-3-small"
EMBEDDING_DIMENSIONS: int = 1536
METRIC: str = "cosine"
STORY_WRITING_MODEL: str = "gpt-4.1-mini-2025-04-14"

# ---------------------------------------------------------------------------
# Perplexity
# ---------------------------------------------------------------------------
LEAD_RESEARCH_MODEL: str = "sonar-pro"
