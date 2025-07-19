"""Configuration package for the timeline reporter project.

This package provides centralized configuration including:
- API keys and credentials
- Model settings and parameters
- Database configuration
- All prompts used across the pipeline
"""

# Import all settings, prompts, curation, discovery, research and deduplication
# configuration
from .curation_config import (
    CRITERIA_EVALUATION_PROMPT_TEMPLATE,
    CRITERIA_WEIGHTS,
    # Curation Configuration
    CURATION_MODEL,
    MAX_LEADS,
    MIN_GROUP_SIZE_FOR_PAIRWISE,
    MIN_LEADS,
    MIN_WEIGHTED_SCORE,
    PAIRWISE_COMPARISON_PROMPT_TEMPLATE,
    PAIRWISE_SCORE_WEIGHT,
    SCORE_SIMILARITY,
    WEIGHTED_SCORE_WEIGHT,
)
from .deduplication_config import (
    # Deduplication Configuration
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    INCLUDE_METADATA,
    METRIC,
    REQUIRED_METADATA_FIELDS,
    SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
    VECTOR_ID_PREFIX,
)
from .discovery_config import (
    DISCOVERY_CATEGORIES,
    DISCOVERY_CATEGORY_INSTRUCTIONS,
    DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
    DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    DISCOVERY_POLITICS_INSTRUCTIONS,
    # Discovery Prompts
    DISCOVERY_SYSTEM_PROMPT,
    # Discovery Configuration
    LEAD_DISCOVERY_MODEL,
    SEARCH_CONTEXT_SIZE,
    # Discovery Timeouts
    DISCOVERY_TIMEOUT_SECONDS,
)
from .research_config import (
    # Research Configuration
    LEAD_RESEARCH_MODEL,
    RESEARCH_INSTRUCTIONS,
    # Research Prompts
    RESEARCH_SYSTEM_PROMPT,
    SEARCH_CONTEXT_SIZE as RESEARCH_SEARCH_CONTEXT_SIZE,
    # Research Timeouts
    RESEARCH_TIMEOUT_SECONDS,
)
from .settings import (
    CLOUD_PROVIDER,
    CLOUD_REGION,
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
)
from .verification_config import (
    MIN_CONTEXT_RELEVANCE_SCORE,
    MIN_SOURCE_CREDIBILITY_SCORE,
    MIN_TOTAL_SCORE,
    VERIFICATION_INSTRUCTIONS,
    VERIFICATION_JSON_FORMAT,
    # Verification Configuration
    VERIFICATION_MODEL,
    # Verification Prompts
    VERIFICATION_SYSTEM_PROMPT,
    VERIFICATION_TEMPERATURE,
)

__all__ = [
    # API Keys
    "OPENAI_API_KEY",
    "PINECONE_API_KEY",
    "PERPLEXITY_API_KEY",
    "MONGODB_URI",
    # Pinecone Configuration
    "PINECONE_INDEX_NAME",
    "CLOUD_PROVIDER",
    "CLOUD_REGION",
    # MongoDB Configuration
    "MONGODB_DATABASE_NAME",
    "MONGODB_COLLECTION_NAME",
    # Discovery Configuration
    "LEAD_DISCOVERY_MODEL",
    "SEARCH_CONTEXT_SIZE",
    "DISCOVERY_CATEGORIES",
    "DISCOVERY_CATEGORY_INSTRUCTIONS",
    "DISCOVERY_TIMEOUT_SECONDS",
    # Curation Configuration
    "CURATION_MODEL",
    "MIN_WEIGHTED_SCORE",
    "MAX_LEADS",
    "MIN_LEADS",
    "SCORE_SIMILARITY",
    "CRITERIA_WEIGHTS",
    "MIN_GROUP_SIZE_FOR_PAIRWISE",
    "WEIGHTED_SCORE_WEIGHT",
    "PAIRWISE_SCORE_WEIGHT",
    # Research Configuration
    "LEAD_RESEARCH_MODEL",
    "RESEARCH_SEARCH_CONTEXT_SIZE",
    "RESEARCH_TIMEOUT_SECONDS",
    # Verification Configuration
    "VERIFICATION_MODEL",
    "VERIFICATION_TEMPERATURE",
    "MIN_SOURCE_CREDIBILITY_SCORE",
    "MIN_CONTEXT_RELEVANCE_SCORE",
    "MIN_TOTAL_SCORE",
    # Deduplication Configuration
    "SIMILARITY_THRESHOLD",
    "TOP_K_RESULTS",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIMENSIONS",
    "METRIC",
    "VECTOR_ID_PREFIX",
    "INCLUDE_METADATA",
    "REQUIRED_METADATA_FIELDS",
    # Discovery Prompts
    "DISCOVERY_SYSTEM_PROMPT",
    "DISCOVERY_POLITICS_INSTRUCTIONS",
    "DISCOVERY_ENVIRONMENT_INSTRUCTIONS",
    "DISCOVERY_ENTERTAINMENT_INSTRUCTIONS",
    # Decision/Curation Prompts
    "CRITERIA_EVALUATION_PROMPT_TEMPLATE",
    "PAIRWISE_COMPARISON_PROMPT_TEMPLATE",
    # Research Prompts
    "RESEARCH_SYSTEM_PROMPT",
    "RESEARCH_INSTRUCTIONS",
    # Verification Prompts
    "VERIFICATION_SYSTEM_PROMPT",
    "VERIFICATION_INSTRUCTIONS",
    "VERIFICATION_JSON_FORMAT",
]
