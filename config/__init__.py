"""Configuration package for the timeline reporter project.

This package provides centralized configuration including:
- API keys and credentials
- Model settings and parameters
- Database configuration
- All prompts used across the pipeline
"""

# Import all settings, prompts, curation, discovery and research configuration
from .curation_config import (
    ALL_CURATION_PROMPTS,
    CRITERIA_EVALUATION_PROMPT_TEMPLATE,
    CRITERIA_WEIGHTS,
    # Curation Configuration
    CURATION_INSTRUCTIONS,
    CURATION_MODEL,
    CURATION_PROMPTS,
    # Decision Prompts
    CURATION_SYSTEM_PROMPT,
    DECISION_PROMPTS,
    MAX_LEADS,
    MIN_GROUP_SIZE_FOR_PAIRWISE,
    MIN_LEADS,
    MIN_WEIGHTED_SCORE,
    PAIRWISE_COMPARISON_PROMPT_TEMPLATE,
    PAIRWISE_SCORE_WEIGHT,
    SCORE_SIMILARITY,
    WEIGHTED_SCORE_WEIGHT,
)
from .discovery_config import (
    ALL_DISCOVERY_PROMPTS,
    DISCOVERY_CATEGORIES,
    DISCOVERY_CATEGORY_INSTRUCTIONS,
    DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
    DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    DISCOVERY_POLITICS_INSTRUCTIONS,
    # Organized Prompt Collections
    DISCOVERY_PROMPTS,
    # Discovery Prompts
    DISCOVERY_SYSTEM_PROMPT,
    # Discovery Configuration
    LEAD_DISCOVERY_MODEL,
    SEARCH_CONTEXT_SIZE,
)
from .research_config import (
    ALL_RESEARCH_PROMPTS,
    # Research Configuration
    LEAD_RESEARCH_MODEL,
    MAX_RESEARCH_RETRIES,
    RESEARCH_INSTRUCTIONS,
    # Organized Prompt Collections
    RESEARCH_PROMPTS,
    # Research Prompts
    RESEARCH_SYSTEM_PROMPT,
    RESEARCH_TIMEOUT_SECONDS,
    STORY_QUALITY_GUIDELINES,
    STORY_WRITING_MODEL,
)
from .settings import (
    CLOUD_PROVIDER,
    CLOUD_REGION,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    # OpenAI Configuration
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
    "EMBEDDING_MODEL",
    "EMBEDDING_DIMENSIONS",
    "METRIC",
    # MongoDB Configuration
    "MONGODB_DATABASE_NAME",
    "MONGODB_COLLECTION_NAME",
    # Discovery Configuration
    "LEAD_DISCOVERY_MODEL",
    "SEARCH_CONTEXT_SIZE",
    "DISCOVERY_CATEGORIES",
    "DISCOVERY_CATEGORY_INSTRUCTIONS",
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
    "STORY_WRITING_MODEL",
    "RESEARCH_TIMEOUT_SECONDS",
    "MAX_RESEARCH_RETRIES",
    "STORY_QUALITY_GUIDELINES",
    # Discovery Prompts
    "DISCOVERY_SYSTEM_PROMPT",
    "DISCOVERY_POLITICS_INSTRUCTIONS",
    "DISCOVERY_ENVIRONMENT_INSTRUCTIONS",
    "DISCOVERY_ENTERTAINMENT_INSTRUCTIONS",
    # Decision/Curation Prompts
    "CURATION_SYSTEM_PROMPT",
    "CURATION_INSTRUCTIONS",
    "CRITERIA_EVALUATION_PROMPT_TEMPLATE",
    "PAIRWISE_COMPARISON_PROMPT_TEMPLATE",
    # Research Prompts
    "RESEARCH_SYSTEM_PROMPT",
    "RESEARCH_INSTRUCTIONS",
    # Organized Prompt Collections
    "DISCOVERY_PROMPTS",
    "DECISION_PROMPTS",
    "RESEARCH_PROMPTS",
    "CURATION_PROMPTS",
    "ALL_CURATION_PROMPTS",
    "ALL_DISCOVERY_PROMPTS",
    "ALL_RESEARCH_PROMPTS",
]
