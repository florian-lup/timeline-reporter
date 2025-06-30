"""Shared test configuration and fixtures."""

import os
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key',
        'PINECONE_API_KEY': 'test-pinecone-key', 
        'PERPLEXITY_API_KEY': 'test-perplexity-key',
        'MONGODB_URI': 'mongodb://test-host:27017/test-db'
    }, clear=False):
        yield


@pytest.fixture
def sample_vector():
    """Sample vector for testing."""
    return [0.1, 0.2, 0.3, 0.4, 0.5] * 300  # 1500 dimensions


@pytest.fixture  
def sample_article_data():
    """Sample article data for testing."""
    return {
        "headline": "Test Article Headline",
        "summary": "This is a test article summary with relevant information.",
        "story": "This is the full story content with detailed information about the topic.",
        "sources": [
            "https://example.com/source1",
            "https://example.com/source2", 
            "https://example.com/source3"
        ]
    }


@pytest.fixture
def sample_research_prompt():
    """Sample research prompt for testing."""
    return "Research the latest developments in artificial intelligence and machine learning" 