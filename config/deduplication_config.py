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
# GPT System and Prompt Configuration
# ---------------------------------------------------------------------------

# JSON Schema for structured output
DEDUPLICATION_SCHEMA = {
    "name": "deduplication_result",
    "schema": {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "enum": ["DUPLICATE", "UNIQUE"],
                "description": "Whether the new lead is a duplicate of existing content or unique"
            }
        },
        "required": ["result"],
        "additionalProperties": False
    }
}

DEDUPLICATION_SYSTEM_PROMPT = """
You are an expert content analyst specializing in detecting duplicate news stories.

Your task is to determine whether a new lead describes the same core story as any existing published story from the past {lookback_hours} hours.

## EVALUATION PROCESS

Follow these steps:

1. Identify the core story: What is the main event, announcement, or development in the new lead?

2. Compare with existing summaries: Does any existing summary cover the same fundamental story?

3. Apply duplicate criteria: A lead is DUPLICATE if it shares:
   - Same primary subject/entity (person, company, organization)
   - Same type of event (announcement, incident, policy change, etc.)
   - Same timeframe (within 24 hours of each other)

4. Ignore surface differences: Different perspectives, additional details, or varied wording do NOT make stories unique if they cover the same core event.

## DECISION CRITERIA

DUPLICATE: The new lead reports on the same underlying story/event as an existing summary
UNIQUE: The new lead introduces a genuinely different story not covered in existing summaries
""".strip()

DEDUPLICATION_PROMPT_TEMPLATE = """
## INPUT DATA

**NEW LEAD:**
{lead_text}

**EXISTING SUMMARIES (Last {lookback_hours} hours):**
{existing_summaries}

""".strip()
