"""Configuration package for the timeline reporter project.

This package provides centralized configuration including:
- API keys and credentials
- Model settings and parameters
- Voice mappings for TTS
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
    # TTS Prompts
    TTS_INSTRUCTIONS,
    TTS_PROMPTS,
)
from .settings import (
    CHAT_MODEL,
    CLOUD_PROVIDER,
    CLOUD_REGION,
    DECISION_MODEL,
    # OpenAI Configuration
    DEEP_RESEARCH_MODEL,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    HOST_VOICE,
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
    REASONING_EFFORT,
    # Voice Mappings
    REPORTER_VOICE,
    # Perplexity Configuration
    RESEARCH_MODEL,
    SEARCH_CONTEXT_SIZE,
    SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
    TTS_MODEL,
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
    "TTS_MODEL",
    "CHAT_MODEL",
    "DECISION_MODEL",
    # Voice Mappings
    "REPORTER_VOICE",
    "HOST_VOICE",
    # Perplexity Configuration
    "RESEARCH_MODEL",
    "SEARCH_CONTEXT_SIZE",
    "REASONING_EFFORT",
    # MongoDB Configuration
    "MONGODB_DATABASE_NAME",
    "MONGODB_COLLECTION_NAME",
    # Discovery Prompts
    "DISCOVERY_SYSTEM_PROMPT",
    "DISCOVERY_INSTRUCTIONS",
    # Decision Prompts
    "DECISION_SYSTEM_PROMPT",
    "DECISION_INSTRUCTIONS",
    # Research Prompts
    "RESEARCH_SYSTEM_PROMPT",
    "RESEARCH_INSTRUCTIONS",
    # TTS Prompts
    "TTS_INSTRUCTIONS",
    # Organized Prompt Collections
    "DISCOVERY_PROMPTS",
    "DECISION_PROMPTS",
    "RESEARCH_PROMPTS",
    "TTS_PROMPTS",
    "ALL_PROMPTS",
]
