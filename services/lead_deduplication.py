"""Service for identifying and removing duplicate leads using vector similarity."""

from clients.openai_client import OpenAIClient
from clients.pinecone_client import PineconeClient
from clients.mongodb_client import MongoDBClient
from config.deduplication_config import (
    INCLUDE_METADATA,
    REQUIRED_METADATA_FIELDS,
    VECTOR_ID_PREFIX,
    DEDUPLICATION_MODEL,
    LOOKBACK_HOURS,
    DEDUPLICATION_SYSTEM_PROMPT,
    DEDUPLICATION_PROMPT_TEMPLATE,
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
    mongodb_client: MongoDBClient | None = None,
) -> list[Lead]:
    """Removes near-duplicate leads based on vector similarity and database comparison.

    First applies vector-based deduplication using Pinecone, then optionally
    compares remaining leads against recent database records using GPT-4o.

    Args:
        leads: List of leads to deduplicate
        openai_client: OpenAI client for embeddings and GPT comparisons
        pinecone_client: Pinecone client for vector similarity search
        mongodb_client: MongoDB client for database comparison (optional)

    Returns:
        List of unique leads after both deduplication layers
    """
    # First layer: Vector-based deduplication
    vector_unique_leads = _vector_deduplication(
        leads,
        openai_client=openai_client,
        pinecone_client=pinecone_client,
    )

    # Second layer: Database comparison using GPT-4o
    if mongodb_client is not None and vector_unique_leads:
        return _database_deduplication(
            vector_unique_leads,
            openai_client=openai_client,
            mongodb_client=mongodb_client,
        )
    
    return vector_unique_leads


# ---------------------------------------------------------------------------
# Deduplication Layers
# ---------------------------------------------------------------------------


def _vector_deduplication(
    leads: list[Lead],
    *,
    openai_client: OpenAIClient,
    pinecone_client: PineconeClient,
) -> list[Lead]:
    """First deduplication layer using vector similarity."""
    unique_leads: list[Lead] = []
    duplicates_found = 0

    logger.info("  🔍 Running vector-based deduplication...")

    for idx, lead in enumerate(leads):
        # Create embedding from the discovered_lead
        vector = openai_client.embed_text(lead.discovered_lead)

        # Query for similar existing leads
        matches = pinecone_client.similarity_search(vector)
        if matches:
            duplicates_found += 1
            first_words = " ".join(lead.discovered_lead.split()[:5]) + "..."
            logger.info(
                "  🔄 Vector duplicate: Lead %d/%d - %s",
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
        logger.info("  🔄 Vector layer: Removed %d duplicates", duplicates_found)
    else:
        logger.info("  ✓ Vector layer: No duplicates found")
    
    return unique_leads


def _database_deduplication(
    leads: list[Lead],
    *,
    openai_client: OpenAIClient,
    mongodb_client: MongoDBClient,
) -> list[Lead]:
    """Second deduplication layer using GPT-4o comparison against database records."""
    logger.info("  🤖 Running GPT-4o database comparison...")
    
    # Get recent stories from database
    recent_stories = mongodb_client.get_recent_stories(hours=LOOKBACK_HOURS)
    
    if not recent_stories:
        logger.info("  ✓ Database layer: No recent stories to compare against")
        return leads
    
    unique_leads: list[Lead] = []
    database_duplicates = 0
    
    for idx, lead in enumerate(leads):
        is_duplicate = _compare_with_database_records(
            lead, 
            recent_stories, 
            openai_client
        )
        
        if is_duplicate:
            database_duplicates += 1
            first_words = " ".join(lead.discovered_lead.split()[:5]) + "..."
            logger.info(
                "  🔄 Database duplicate: Lead %d/%d - %s",
                idx + 1,
                len(leads),
                first_words,
            )
        else:
            unique_leads.append(lead)
    
    if database_duplicates > 0:
        logger.info("  🔄 Database layer: Removed %d duplicates", database_duplicates)
    else:
        logger.info("  ✓ Database layer: No duplicates found")
    
    return unique_leads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _compare_with_database_records(
    lead: Lead, 
    recent_stories: list[dict], 
    openai_client: OpenAIClient
) -> bool:
    """Use GPT-4o to compare a lead against recent database records.
    
    Returns True if the lead is similar to any existing record.
    """
    if not recent_stories:
        return False
        
    # Prepare summaries for comparison
    story_summaries = []
    for story in recent_stories:
        summary = story.get('summary', '')
        if summary:  # Only include non-empty summaries
            story_summaries.append(summary)
    
    # Create comparison prompt using centralized template
    existing_summaries_text = chr(10).join([f"{i+1}. {summary}" for i, summary in enumerate(story_summaries)])
    
    user_prompt = DEDUPLICATION_PROMPT_TEMPLATE.format(
        lead_text=lead.discovered_lead,
        lookback_hours=LOOKBACK_HOURS,
        existing_summaries=existing_summaries_text,
    )
    
    # Combine system prompt with user prompt
    full_prompt = f"{DEDUPLICATION_SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        response = openai_client.chat_completion(
            prompt=full_prompt,
            model=DEDUPLICATION_MODEL,
        )
        
        return response.strip().upper() == "DUPLICATE"
        
    except Exception as e:
        logger.warning("  ⚠️ GPT comparison failed: %s. Treating as unique.", str(e))
        return False


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
