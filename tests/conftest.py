"""Shared test configuration and fixtures."""

import json
import os
from unittest.mock import Mock, patch

import pytest

from models import Lead, Story


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-openai-key",
            "PINECONE_API_KEY": "test-pinecone-key",
            "PERPLEXITY_API_KEY": "test-perplexity-key",
            "MONGODB_URI": "mongodb://test-host:27017/test-db",
        },
        clear=False,
    ):
        yield


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_client.embed_text.return_value = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
    mock_client.chat_completion.return_value = "1, 2, 3"
    return mock_client


@pytest.fixture
def mock_pinecone_client():
    """Mock Pinecone client for testing."""
    mock_client = Mock()
    mock_client.similarity_search.return_value = []  # No duplicates by default
    mock_client.upsert_vector.return_value = None
    return mock_client


@pytest.fixture
def mock_perplexity_client():
    """Mock Perplexity client for testing."""
    mock_client = Mock()

    # Mock discovery response
    discovery_response = json.dumps(
        [
                    {"title": "Climate Summit 2024: World leaders meet to discuss climate action and set ambitious targets for carbon reduction."},
        {"title": "AI Breakthrough Announced: New AI model shows remarkable capabilities in medical diagnosis and drug discovery."},
        ]
    )
    mock_client.lead_discovery.return_value = discovery_response

    # Mock research response
    research_response = json.dumps(
        {
            "headline": "Breaking News Story",
            "summary": "Important lead summary",
            "body": "Full story body with detailed information.",
            "sources": ["https://example.com/source1", "https://example.com/source2"],
        }
    )
    mock_client.research.return_value = research_response

    return mock_client


@pytest.fixture
def mock_mongodb_client():
    """Mock MongoDB client for testing."""
    mock_client = Mock()
    mock_client.insert_story.return_value = "64a7b8c9d1e2f3a4b5c6d7e8"
    return mock_client


@pytest.fixture
def sample_lead():
    """Sample Lead object for testing."""
    return Lead(
        discovered_lead="Sample Lead Title: This is a sample lead summary for testing purposes.",
    )


@pytest.fixture
def sample_leads():
    """Sample list of Lead objects for testing."""
    return [
        Lead(
            discovered_lead="Technology Breakthrough: Major advancement in artificial intelligence technology announced.",
        ),
        Lead(
            discovered_lead="Climate Change Update: New climate research reveals important environmental findings.",
        ),
        Lead(
            discovered_lead="Economic Development: Significant economic changes affecting global markets.",
        ),
    ]


@pytest.fixture
def sample_story():
    """Sample Story object for testing."""
    return Story(
        headline="Breaking: Major Climate Summit Concluded",
        summary="World leaders reach historic agreement on carbon reduction targets.",
        body="In a landmark decision today, world leaders...",
        tag="environment",
        sources=[
            "https://example.com/climate-news",
            "https://example.com/summit-report",
        ],
    )


@pytest.fixture
def sample_stories():
    """Sample list of Story objects for testing."""
    return [
        Story(
            headline="Technology Breakthrough in AI",
            summary="Researchers announce major advancement in artificial intelligence.",
            body="Scientists at leading research institutions have...",
            tag="technology",
            sources=[
                "https://example.com/tech-news",
                "https://example.com/ai-research",
            ],
        ),
        Story(
            headline="Climate Action Summit Results",
            summary="Global climate summit concludes with new agreements.",
            body="The three-day climate summit has concluded with...",
            tag="environment",
            sources=[
                "https://example.com/climate-summit",
                "https://example.com/environment",
            ],
        ),
    ]


@pytest.fixture
def sample_discovery_response():
    """Sample discovery response from Perplexity API."""
    return json.dumps([
        {"discovered_lead": "Climate Summit 2024: World leaders meet to discuss climate action and set ambitious targets for carbon reduction."},
        {"discovered_lead": "AI Breakthrough Announced: New AI model shows remarkable capabilities in medical diagnosis and drug discovery."},
    ])
