"""Shared test configuration and fixtures."""

import os
import json
import pytest
from unittest.mock import Mock, patch
from utils import Event, Article


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
def sample_embedding():
    """Sample OpenAI embedding vector (1536 dimensions)."""
    return [0.1] * 1536


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


@pytest.fixture
def sample_event():
    """Sample Event object for testing."""
    return Event(
        title="Sample Event Title",
        summary="This is a sample event summary for testing purposes."
    )


@pytest.fixture
def sample_events():
    """Sample list of Event objects for testing."""
    return [
        Event(
            title="Technology Breakthrough",
            summary="Major advancement in artificial intelligence technology announced."
        ),
        Event(
            title="Climate Change Update", 
            summary="New climate research reveals important environmental findings."
        ),
        Event(
            title="Economic Development",
            summary="Significant economic changes affecting global markets."
        )
    ]


@pytest.fixture
def sample_article():
    """Sample Article object for testing."""
    return Article(
        headline="Sample Article Headline",
        summary="This is a sample article summary.",
        story="This is the full story content with detailed information.",
        sources=["https://example.com/source1", "https://example.com/source2"],
        broadcast=b"",
        reporter=""
    )


@pytest.fixture
def sample_articles():
    """Sample list of Article objects for testing."""
    return [
        Article(
            headline="Tech News Article",
            summary="Article about technology developments",
            story="Full story about technology developments in the industry.",
            sources=["https://example.com/tech1", "https://example.com/tech2"],
            broadcast=b"",
            reporter=""
        ),
        Article(
            headline="Climate News Article",
            summary="Article about climate change",
            story="Full story about recent climate change developments.",
            sources=["https://example.com/climate1"],
            broadcast=b"",
            reporter=""
        )
    ]


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_client.embed_text.return_value = [0.1] * 1536
    mock_client.chat_completion.return_value = "Test chat completion response"
    mock_client.text_to_speech.return_value = b"test_audio_data"
    return mock_client


@pytest.fixture
def mock_perplexity_client():
    """Mock Perplexity client for testing."""
    mock_client = Mock()
    mock_client.deep_research.return_value = json.dumps([
        {"title": "Test Event", "summary": "Test summary"}
    ])
    mock_client.research.return_value = json.dumps({
        "headline": "Test Headline",
        "summary": "Test summary",
        "story": "Test story content",
        "sources": ["https://example.com/test"]
    })
    return mock_client


@pytest.fixture
def mock_pinecone_client():
    """Mock Pinecone client for testing."""
    mock_client = Mock()
    mock_client.similarity_search.return_value = []  # No similar vectors by default
    mock_client.upsert_vector.return_value = True
    return mock_client


@pytest.fixture
def mock_mongodb_client():
    """Mock MongoDB client for testing."""
    mock_client = Mock()
    mock_client.insert_article.return_value = "test_object_id_123"
    mock_client.find_articles.return_value = []
    return mock_client


@pytest.fixture
def all_mock_clients(mock_openai_client, mock_perplexity_client, mock_pinecone_client, mock_mongodb_client):
    """All mock clients in a dictionary for easy access."""
    return {
        'openai': mock_openai_client,
        'perplexity': mock_perplexity_client,
        'pinecone': mock_pinecone_client,
        'mongodb': mock_mongodb_client
    }


@pytest.fixture
def sample_discovery_response():
    """Sample response from discovery service."""
    return json.dumps([
        {
            "title": "AI Breakthrough in Healthcare",
            "summary": "Revolutionary AI system shows 99% accuracy in medical diagnosis."
        },
        {
            "title": "Climate Summit Reaches Agreement",
            "summary": "World leaders agree on ambitious carbon reduction targets."
        }
    ])


@pytest.fixture
def sample_research_response():
    """Sample response from research service."""
    return json.dumps({
        "headline": "Breakthrough AI System Transforms Medical Diagnosis",
        "summary": "A revolutionary artificial intelligence system has achieved unprecedented accuracy in medical diagnosis, potentially transforming healthcare delivery.",
        "story": "Researchers at leading medical institutions have developed an AI system that demonstrates 99% accuracy in diagnosing a wide range of medical conditions. The system uses advanced machine learning algorithms trained on millions of medical records and diagnostic images.",
        "sources": [
            "https://example.com/medical-ai-breakthrough",
            "https://example.com/healthcare-technology-news",
            "https://example.com/ai-medical-diagnosis"
        ]
    })


@pytest.fixture
def sample_malformed_json():
    """Sample malformed JSON for error testing."""
    return '{"title": "Test", "summary": "Test summary"'  # Missing closing brace 