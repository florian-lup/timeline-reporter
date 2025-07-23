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

# ---------------------------------------------------------------------------
# GPT-4o Deduplication Configuration
# ---------------------------------------------------------------------------
DEDUPLICATION_MODEL: str = "o4-mini-2025-04-16"
LOOKBACK_HOURS: int = 24  # Hours to look back in database for comparison

# ---------------------------------------------------------------------------
# GPT Comparison Prompt Template
# ---------------------------------------------------------------------------
DEDUPLICATION_PROMPT_TEMPLATE: str = """You are comparing a new lead against existing story summaries to detect duplicates.

NEW LEAD:
"{lead_text}"

EXISTING STORY SUMMARIES FROM LAST {lookback_hours} HOURS:
{existing_summaries}

TASK: Determine if the new lead covers the same core event/story as any existing summary.
Consider that leads are brief discovery summaries while existing records are detailed story summaries.
Focus on the fundamental event or topic, not minor details or different perspectives.

Respond with ONLY "DUPLICATE" if the lead matches an existing story, or "UNIQUE" if it's genuinely new.
"""
