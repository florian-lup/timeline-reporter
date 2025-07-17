"""Configuration package for the timeline reporter project.

This package provides centralized configuration including:
- API keys and credentials
- Model settings and parameters
- Database configuration
- All prompts used across the pipeline
"""

# Import all settings
# Import all prompts
from .prompts import (
    ALL_PROMPTS,
    DECISION_INSTRUCTIONS,
    DECISION_PROMPTS,
    # Decision Prompts
    DECISION_SYSTEM_PROMPT,
    DISCOVERY_INSTRUCTIONS,
    # Organized Prompt Collections
    DISCOVERY_PROMPTS,
    # Discovery Prompts
    DISCOVERY_SYSTEM_PROMPT,
    RESEARCH_INSTRUCTIONS,
    RESEARCH_PROMPTS,
    # Research Prompts
    RESEARCH_SYSTEM_PROMPT,
)
from .settings import (
    CHAT_MODEL,
    CLOUD_PROVIDER,
    CLOUD_REGION,
    CURATION_MODEL,
    # OpenAI Configuration
    DEEP_RESEARCH_MODEL,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    HYBRID_MAX_LEADS,
    HYBRID_MIN_LEADS,
    # Lead Curation Configuration
    HYBRID_MIN_WEIGHTED_SCORE,
    HYBRID_SCORE_SIMILARITY,
    METRIC,
    MONGODB_COLLECTION_NAME,
    # MongoDB Configuration
    MONGODB_DATABASE_NAME,
    MONGODB_URI,
    # API Keys
    OPENAI_API_KEY,
    PERPLEXITY_API_KEY,
    PINECONE_API_KEY,
    # Pinecone Configuration
    PINECONE_INDEX_NAME,
    # Perplexity Configuration
    RESEARCH_MODEL,
    SEARCH_CONTEXT_SIZE,
    SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
)

__all__ = [
    # API Keys
    "OPENAI_API_KEY",
    "PINECONE_API_KEY",
    "PERPLEXITY_API_KEY",
    "MONGODB_URI",
    # Pinecone Configuration
    "PINECONE_INDEX_NAME",
    "SIMILARITY_THRESHOLD",
    "TOP_K_RESULTS",
    "CLOUD_PROVIDER",
    "CLOUD_REGION",
    # OpenAI Configuration
    "DEEP_RESEARCH_MODEL",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIMENSIONS",
    "METRIC",
    "CHAT_MODEL",
    "CURATION_MODEL",
    # Perplexity Configuration
    "RESEARCH_MODEL",
    "SEARCH_CONTEXT_SIZE",
    # MongoDB Configuration
    "MONGODB_DATABASE_NAME",
    "MONGODB_COLLECTION_NAME",
    # Lead Curation Configuration
    "HYBRID_MIN_WEIGHTED_SCORE",
    "HYBRID_MAX_LEADS",
    "HYBRID_MIN_LEADS",
    "HYBRID_SCORE_SIMILARITY",
    # Discovery Prompts
    "DISCOVERY_SYSTEM_PROMPT",
    "DISCOVERY_INSTRUCTIONS",
    # Decision Prompts
    "DECISION_SYSTEM_PROMPT",
    "DECISION_INSTRUCTIONS",
    # Research Prompts
    "RESEARCH_SYSTEM_PROMPT",
    "RESEARCH_INSTRUCTIONS",
    # Organized Prompt Collections
    "DISCOVERY_PROMPTS",
    "DECISION_PROMPTS",
    "RESEARCH_PROMPTS",
    "ALL_PROMPTS",
]
