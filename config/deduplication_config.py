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
BATCH_SIZE: int = 100  # Batch size for processing leads
MAX_RETRIES: int = 3  # Maximum retries for embedding/vector operations

# ---------------------------------------------------------------------------
# Deduplication Behavior
# ---------------------------------------------------------------------------
PRESERVE_ORIGINAL_ORDER: bool = True  # Maintain order of non-duplicate leads
INCLUDE_METADATA: bool = True  # Store lead metadata with vectors

# ---------------------------------------------------------------------------
# Metadata Configuration
# ---------------------------------------------------------------------------
REQUIRED_METADATA_FIELDS = [
    "tip",
    "date",
]

OPTIONAL_METADATA_FIELDS = [
    "source",
    "category",
    "confidence",
]

# ---------------------------------------------------------------------------
# Performance Configuration
# ---------------------------------------------------------------------------
EMBEDDING_TIMEOUT_SECONDS: int = 30  # Timeout for embedding generation
SIMILARITY_SEARCH_TIMEOUT_SECONDS: int = 10  # Timeout for similarity search
UPSERT_TIMEOUT_SECONDS: int = 30  # Timeout for vector upsert operations

# ---------------------------------------------------------------------------
# All deduplication configuration for easy access
# ---------------------------------------------------------------------------
ALL_DEDUPLICATION_CONFIG = {
    "similarity": {
        "threshold": SIMILARITY_THRESHOLD,
        "top_k": TOP_K_RESULTS,
        "metric": METRIC,
    },
    "embedding": {
        "model": EMBEDDING_MODEL,
        "dimensions": EMBEDDING_DIMENSIONS,
    },
    "vector_storage": {
        "id_prefix": VECTOR_ID_PREFIX,
        "batch_size": BATCH_SIZE,
        "max_retries": MAX_RETRIES,
    },
    "behavior": {
        "preserve_order": PRESERVE_ORIGINAL_ORDER,
        "include_metadata": INCLUDE_METADATA,
    },
    "timeouts": {
        "embedding": EMBEDDING_TIMEOUT_SECONDS,
        "search": SIMILARITY_SEARCH_TIMEOUT_SECONDS,
        "upsert": UPSERT_TIMEOUT_SECONDS,
    },
}
