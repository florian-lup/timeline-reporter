"""Service for identifying and removing duplicate leads using vector similarity."""

from clients.openai_client import OpenAIClient
from clients.pinecone_client import PineconeClient
from config.deduplication_config import (
    INCLUDE_METADATA,
    REQUIRED_METADATA_FIELDS,
    VECTOR_ID_PREFIX,
)
from models.core import Lead
from utils import logger

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def deduplicate_leads(
    leads: list[Lead],
    *,
    openai_client: OpenAIClient,
    pinecone_client: PineconeClient,
) -> list[Lead]:
    """Removes near-duplicate leads based on vector similarity.

    Each lead's title is embedded and compared against existing vectors in
    Pinecone. Anything with a similarity ≥ threshold is dropped.

    Uses centralized configuration for similarity thresholds, vector storage,
    and metadata handling.
    """
    unique_leads: list[Lead] = []
    duplicates_found = 0

    for idx, lead in enumerate(leads):
        # Create embedding from the title
        vector = openai_client.embed_text(lead.title)

        # Query for similar existing leads
        matches = pinecone_client.similarity_search(vector)
        if matches:
            duplicates_found += 1
            first_words = " ".join(lead.title.split()[:5]) + "..."
            logger.info(
                "  🔄 Duplicate detected: Lead %d/%d - %s (similarity match found)",
                idx + 1,
                len(leads),
                first_words,
            )
            continue

        # Generate vector ID using centralized configuration
        vector_id = f"{VECTOR_ID_PREFIX}-{idx}"

        # Prepare metadata using centralized configuration
        metadata = _prepare_metadata(lead) if INCLUDE_METADATA else {}

        # Upsert and keep the unique lead
        pinecone_client.upsert_vector(
            vector_id,
            vector,
            metadata=metadata,
        )
        unique_leads.append(lead)

    if duplicates_found > 0:
        logger.info("  🔄 Removed %d duplicate leads", duplicates_found)
    else:
        logger.info("  ✓ No duplicates found - all leads are unique")
    return unique_leads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _prepare_metadata(lead: Lead) -> dict[str, str]:
    """Prepare metadata for vector storage using centralized configuration.

    Only includes fields specified in the required metadata configuration.
    """
    metadata = {}

    # Add required fields
    for field in REQUIRED_METADATA_FIELDS:
        if hasattr(lead, field):
            value = getattr(lead, field)
            # Convert to string for Pinecone storage
            metadata[field] = str(value) if value is not None else ""

    return metadata
