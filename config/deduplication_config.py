"""Centralized configuration for lead deduplication system.

This module contains all settings and configuration data
related to lead deduplication using vector similarity.
"""

# ---------------------------------------------------------------------------
# Vector Similarity Configuration
# ---------------------------------------------------------------------------
SIMILARITY_THRESHOLD: float = 0.8  # Threshold for considering leads as duplicates
TOP_K_RESULTS: int = 5  # Maximum number of similarity search results

# ---------------------------------------------------------------------------
# Embedding Configuration
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = "text-embedding-3-small"
EMBEDDING_DIMENSIONS: int = 1536
METRIC: str = "cosine"  # Distance metric for vector similarity

# ---------------------------------------------------------------------------
# Vector Storage Configuration
# ---------------------------------------------------------------------------
VECTOR_ID_PREFIX: str = "lead"  # Prefix for vector IDs in Pinecone

# ---------------------------------------------------------------------------
# Deduplication Behavior
# ---------------------------------------------------------------------------
INCLUDE_METADATA: bool = True  # Store lead metadata with vectors

# ---------------------------------------------------------------------------
# Metadata Configuration
# ---------------------------------------------------------------------------
REQUIRED_METADATA_FIELDS = [
    "discovered_lead",
    "date",
]
