"""Configuration package for the timeline reporter project.

This package provides centralized configuration including:
- API keys and credentials
- Model settings and parameters  
- Voice mappings for TTS
- Database configuration
- All prompts used across the pipeline
"""

# Import all settings
from .settings import (
    # API Keys
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PERPLEXITY_API_KEY,
    MONGODB_URI,
    
    # Pinecone Configuration
    PINECONE_INDEX_NAME,
    SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
    CLOUD_PROVIDER,
    CLOUD_REGION,
    
    # OpenAI Configuration
    DEEP_RESEARCH_MODEL,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    METRIC,
    TTS_MODEL,
    CHAT_MODEL,
    
    # Voice Mappings
    REPORTER_VOICE,
    HOST_VOICE,
    
    # Perplexity Configuration
    RESEARCH_MODEL,
    SEARCH_CONTEXT_SIZE,
    REASONING_EFFORT,
    
    # MongoDB Configuration
    MONGODB_DATABASE_NAME,
    MONGODB_COLLECTION_NAME,
)

# Import all prompts
from .prompts import (
    # Discovery Prompts
    DISCOVERY_SYSTEM_PROMPT,
    DISCOVERY_INSTRUCTIONS,
    
    # Research Prompts
    RESEARCH_SYSTEM_PROMPT,
    RESEARCH_INSTRUCTIONS,
    
    # TTS Prompts
    TTS_INSTRUCTIONS,
    
    # Organized Prompt Collections
    DISCOVERY_PROMPTS,
    RESEARCH_PROMPTS,
    TTS_PROMPTS,
    ALL_PROMPTS,
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
    
    # Research Prompts
    "RESEARCH_SYSTEM_PROMPT",
    "RESEARCH_INSTRUCTIONS",
    
    # TTS Prompts
    "TTS_INSTRUCTIONS",
    
    # Organized Prompt Collections
    "DISCOVERY_PROMPTS",
    "RESEARCH_PROMPTS",
    "TTS_PROMPTS",
    "ALL_PROMPTS",
]
