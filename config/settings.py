"""Centralised configuration settings for the project."""

from __future__ import annotations

import os

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from `.env`
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
MONGODB_COLLECTION_NAME_AUDIO = os.getenv("MONGODB_COLLECTION_NAME_AUDIO")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
CLOUD_PROVIDER = os.getenv("CLOUD_PROVIDER")
CLOUD_REGION = os.getenv("CLOUD_REGION")
