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
CLOUD_PROVIDER: str = "aws"
CLOUD_REGION: str = "us-east-1"

# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = "text-embedding-3-small"
EMBEDDING_DIMENSIONS: int = 1536
METRIC: str = "cosine"
CHAT_MODEL: str = "gpt-4.1-mini-2025-04-14"
CURATION_MODEL: str = "o4-mini-2025-04-16"

# ---------------------------------------------------------------------------
# Perplexity
# ---------------------------------------------------------------------------
LEAD_RESEARCH_MODEL: str = "sonar-pro"
LEAD_DISCOVERY_MODEL: str = "sonar-reasoning-pro"
SEARCH_CONTEXT_SIZE: str = "high"

# ---------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------
MONGODB_DATABASE_NAME: str = "breaking-news"
MONGODB_COLLECTION_NAME: str = "stories"

# ---------------------------------------------------------------------------
# Lead Curation
# ---------------------------------------------------------------------------
HYBRID_MIN_WEIGHTED_SCORE: float = 6.0  # Minimum score for lead consideration
HYBRID_MAX_LEADS: int = 5  # Maximum number of leads to select
HYBRID_MIN_LEADS: int = 3  # Minimum number of leads to select
HYBRID_SCORE_SIMILARITY: float = 0.5  # Score threshold for pairwise comparison
