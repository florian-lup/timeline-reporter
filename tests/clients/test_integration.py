"""Integration tests for client functionality."""

import json
from unittest.mock import Mock, patch

import pytest

from clients import MongoDBClient, OpenAIClient, PerplexityClient, PineconeClient
from models import Story


@pytest.mark.integration
class TestClientIntegration:
    """Integration tests showing how clients work together."""

    def test_openai_embedding_to_pinecone_workflow(self):
        """Test workflow from text embedding to Pinecone storage."""
        with (
            patch("clients.openai_client.OpenAI") as mock_openai,
            patch("clients.pinecone_client.Pinecone") as mock_pinecone,
            patch("clients.openai_client.OPENAI_API_KEY", "test-key"),
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-key"),
        ):
            # Setup OpenAI mock
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_embedding_response = Mock()
            mock_embedding_response.data = [
                Mock(embedding=[0.1] * 1536)
            ]  # Sample embedding
            mock_openai_instance.embeddings.create.return_value = (
                mock_embedding_response
            )

            # Setup Pinecone mock
            mock_pinecone_instance = Mock()
            mock_pinecone.return_value = mock_pinecone_instance
            mock_index = Mock()
            # Mock query response with proper matches format
            mock_query_result = Mock()
            mock_query_result.matches = []  # No matches for this test
            mock_index.query.return_value = mock_query_result
            mock_pinecone_instance.Index.return_value = mock_index
            # Mock list_indexes to return proper format
            mock_list_result = Mock()
            mock_list_result.names.return_value = ["existing-index"]
            mock_pinecone_instance.list_indexes.return_value = mock_list_result

            # Test the workflow
            openai_client = OpenAIClient()
            pinecone_client = PineconeClient()

            # 1. Generate embedding
            test_text = "This is a test lead for embedding"
            embedding = openai_client.embed_text(test_text)

            # 2. Store in Pinecone
            pinecone_client.upsert_vector(
                "test-lead-123", embedding, {"content": test_text}
            )

            # 3. Search for similar events
            pinecone_client.similarity_search(embedding)

            # Verify calls
            mock_openai_instance.embeddings.create.assert_called_once()
            mock_index.upsert.assert_called_once()
            mock_index.query.assert_called_once()

            # Verify data flow
            assert len(embedding) == 1536
            # Verify that upsert was called (specific parameter checking omitted for
            # simplicity)

    def test_perplexity_research_integration(self):
        """Test Perplexity client research functionality."""
        with (
            patch("clients.perplexity_client.httpx.Client") as mock_httpx,
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-key"),
        ):
            # Setup HTTP client mock
            mock_http_client = Mock()
            mock_response = Mock()
            research_data = {
                "context": (
                    "Comprehensive research context about breaking technology news"
                ),
                "sources": [
                    "https://example.com/source1",
                    "https://example.com/source2",
                ],
            }
            mock_response.json.return_value = {
                "choices": [{"message": {"content": json.dumps(research_data)}}]
            }
            mock_response.raise_for_status.return_value = None
            mock_httpx.return_value.__enter__.return_value = mock_http_client
            mock_http_client.post.return_value = mock_response

            # Test research
            perplexity_client = PerplexityClient()
            research_prompt = "Research this lead: Breaking news about technology"
            result = perplexity_client.lead_research(research_prompt)

            # Verify API call
            mock_http_client.post.assert_called_once()
            call_args = mock_http_client.post.call_args
            assert (
                "senior investigative research analyst"
                in call_args[1]["json"]["messages"][0]["content"]
            )

            # Verify result parsing - lead research returns context + sources
            result_data = json.loads(result)
            assert result_data["context"] == (
                "Comprehensive research context about breaking technology news"
            )
            assert len(result_data["sources"]) == 2

    def test_mongodb_story_storage_integration(self):
        """Test MongoDB story storage functionality."""
        with (
            patch("clients.mongodb_client.MongoClient") as mock_mongo,
            patch("clients.mongodb_client.MONGODB_URI", "test-uri"),
        ):
            # Setup MongoDB mock
            mock_mongo_instance = Mock()
            mock_mongo.return_value = mock_mongo_instance
            mock_db = Mock()
            mock_collection = Mock()
            mock_mongo_instance.__getitem__ = Mock(return_value=mock_db)
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_result = Mock()
            mock_result.inserted_id = "507f1f77bcf86cd799439011"
            mock_collection.insert_one.return_value = mock_result

            # Test story storage
            mongodb_client = MongoDBClient()
            test_story = {
                "headline": "Test Story",
                "summary": "Test summary",
                "body": "Test story content",
                "sources": ["https://example.com"],
                "date": "2024-01-01",
            }

            result_id = mongodb_client.insert_story(test_story)

            # Verify storage
            mock_collection.insert_one.assert_called_once_with(test_story)
            assert result_id == "507f1f77bcf86cd799439011"

    def test_story_model_integration(self):
        """Test Story model integration with updated fields."""
        # Test creating Story with all required fields
        story = Story(
            headline="Test Headline",
            summary="Test summary",
            body="Test story content",
            tag="other",
            sources=["https://example.com"],
        )

        assert story.headline == "Test Headline"
        assert story.summary == "Test summary"
        assert story.body == "Test story content"
        assert story.sources == ["https://example.com"]

        # Test converting to dict for MongoDB storage
        story_dict = story.__dict__
        expected_keys = {
            "headline",
            "summary",
            "body",
            "tag",
            "sources",
            "date",
        }
        actual_keys = set(story_dict.keys())
        assert actual_keys == expected_keys

        # Test that all fields are present (no None values)
        for key, value in story_dict.items():
            assert value is not None, f"Field {key} should not be None"

    def test_research_to_storage_pipeline_integration(self):
        """Test integration from research service through to storage."""
        with (
            patch("clients.perplexity_client.httpx.Client") as mock_httpx,
            patch("clients.mongodb_client.MongoClient") as mock_mongo,
            patch("clients.openai_client.OpenAI") as mock_openai,
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-key"),
            patch("clients.mongodb_client.MONGODB_URI", "test-uri"),
            patch("clients.openai_client.OPENAI_API_KEY", "test-openai-key"),
        ):
            # Setup Perplexity mock (lead research)
            mock_http_client = Mock()
            mock_response = Mock()
            research_data = {
                "context": "Enhanced context about breaking news from research",
                "sources": ["https://source.com"],
            }
            mock_response.json.return_value = {
                "choices": [{"message": {"content": json.dumps(research_data)}}]
            }
            mock_response.raise_for_status.return_value = None
            mock_httpx.return_value.__enter__.return_value = mock_http_client
            mock_http_client.post.return_value = mock_response

            # Setup OpenAI mock (story writing)
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            story_data = {
                "headline": "Breaking News",
                "summary": "Important lead summary",
                "body": "Full story details...",
            }
            mock_openai_instance.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content=json.dumps(story_data)))]
            )

            # MongoDB storage
            mock_mongo_instance = Mock()
            mock_mongo.return_value = mock_mongo_instance
            mock_db = Mock()
            mock_collection = Mock()
            mock_mongo_instance.__getitem__ = Mock(return_value=mock_db)
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            mock_result = Mock()
            mock_result.inserted_id = "507f1f77bcf86cd799439013"
            mock_collection.insert_one.return_value = mock_result

            # Execute full pipeline
            from clients import OpenAIClient
            from models import Lead
            from services import research_lead, write_stories

            perplexity_client = PerplexityClient()
            mongodb_client = MongoDBClient()
            openai_client = OpenAIClient()

            # 1. Research phase - enhance leads with context
            test_leads = [Lead(tip="Breaking News: Important lead")]
            researched_leads = research_lead(
                test_leads, perplexity_client=perplexity_client
            )

            # 2. Writing phase - convert enhanced leads to stories
            stories = write_stories(researched_leads, openai_client=openai_client)

            # 3. Storage phase
            for story in stories:
                mongodb_client.insert_story(story.__dict__)

            # Verify end-to-end pipeline
            assert len(researched_leads) == 1
            assert len(stories) == 1

            # Check research enhanced the lead
            researched_lead = researched_leads[0]
            assert researched_lead.context == (
                "Enhanced context about breaking news from research"
            )
            assert researched_lead.sources == ["https://source.com"]

            # Check story was created from researched lead
            final_story = stories[0]
            assert final_story.headline == "Breaking News"
            assert final_story.summary == "Important lead summary"
            assert final_story.body == "Full story details..."
            # Sources preserved from research
            assert final_story.sources == ["https://source.com"]

            # Verify all services were called
            # Perplexity research
            mock_http_client.post.assert_called_once()
            # OpenAI story writing
            mock_openai_instance.chat.completions.create.assert_called_once()
            # MongoDB storage
            mock_collection.insert_one.assert_called_once()

    def test_similarity_search_workflow(self):
        """Test workflow for finding similar stories."""
        with (
            patch("clients.openai_client.OpenAI") as mock_openai,
            patch("clients.pinecone_client.Pinecone") as mock_pinecone,
            patch("clients.mongodb_client.MongoClient"),
            patch("clients.openai_client.OPENAI_API_KEY", "test-key"),
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-key"),
            patch("clients.mongodb_client.MONGODB_URI", "test-uri"),
        ):
            # Setup mocks
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_embedding_response = Mock()
            mock_embedding_response.data = [Mock(embedding=[0.5] * 1536)]
            mock_openai_instance.embeddings.create.return_value = (
                mock_embedding_response
            )

            mock_pinecone_instance = Mock()
            mock_pinecone.return_value = mock_pinecone_instance
            mock_index = Mock()
            mock_index.query.return_value = Mock(
                matches=[
                    Mock(id="similar-lead-1", score=0.9),
                    Mock(id="similar-lead-2", score=0.8),
                ]
            )
            mock_pinecone_instance.Index.return_value = mock_index
            # Mock list_indexes to return proper format
            mock_list_result = Mock()
            mock_list_result.names.return_value = ["existing-index"]
            mock_pinecone_instance.list_indexes.return_value = mock_list_result

            # Test similarity search workflow
            openai_client = OpenAIClient()
            pinecone_client = PineconeClient()

            # Search for similar content
            query_text = "Climate summit discusses global warming solutions"
            embedding = openai_client.embed_text(query_text)
            similar_events = pinecone_client.similarity_search(embedding)

            # Verify workflow
            assert len(similar_events) == 2
            assert similar_events[0][0] == "similar-lead-1"  # ID is first element
            assert similar_events[0][1] == 0.9  # Score is second element

    def test_client_error_handling_integration(self):
        """Test error handling across client integrations."""
        with (
            patch("clients.openai_client.OpenAI") as mock_openai,
            patch("clients.openai_client.OPENAI_API_KEY", "test-key"),
        ):
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_openai_instance.embeddings.create.side_effect = Exception(
                "API rate limit exceeded"
            )

            openai_client = OpenAIClient()

            # Test that exceptions propagate correctly
            with pytest.raises(Exception, match="API rate limit exceeded"):
                openai_client.embed_text("test text")

    def test_multimodal_client_workflow(self):
        """Test workflow combining multiple clients."""
        with (
            patch("clients.perplexity_client.httpx.Client") as mock_httpx,
            patch("clients.openai_client.OpenAI") as mock_openai,
            patch("clients.pinecone_client.Pinecone") as mock_pinecone,
            patch("clients.perplexity_client.PERPLEXITY_API_KEY", "test-key"),
            patch("clients.openai_client.OPENAI_API_KEY", "test-key"),
            patch("clients.pinecone_client.PINECONE_API_KEY", "test-key"),
        ):
            # Setup all client mocks
            # Perplexity (discovery)
            mock_http_client = Mock()
            mock_discovery_response = Mock()
            mock_discovery_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                [
                                    {
                                        "title": "Climate News",
                                        "summary": "Important update",
                                    }
                                ]
                            )
                        }
                    }
                ]
            }
            mock_discovery_response.raise_for_status.return_value = None
            mock_httpx.return_value.__enter__.return_value = mock_http_client
            mock_http_client.post.return_value = mock_discovery_response

            # OpenAI (embeddings)
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_embedding_response = Mock()
            mock_embedding_response.data = [Mock(embedding=[0.3] * 1536)]
            mock_openai_instance.embeddings.create.return_value = (
                mock_embedding_response
            )

            # Pinecone (similarity search)
            mock_pinecone_instance = Mock()
            mock_pinecone.return_value = mock_pinecone_instance
            mock_index = Mock()
            mock_index.query.return_value = Mock(matches=[])  # No similar events
            mock_pinecone_instance.Index.return_value = mock_index
            # Mock list_indexes to return proper format
            mock_list_result = Mock()
            mock_list_result.names.return_value = ["existing-index"]
            mock_pinecone_instance.list_indexes.return_value = mock_list_result

            # Test multimodal workflow
            perplexity_client = PerplexityClient()
            openai_client = OpenAIClient()
            pinecone_client = PineconeClient()

            # 1. Discovery
            discovery_result = perplexity_client.lead_discovery(
                "Find recent climate news"
            )
            events = json.loads(discovery_result)

            # 2. Embedding generation
            event_text = f"{events[0]['title']} {events[0]['summary']}"
            embedding = openai_client.embed_text(event_text)

            # 3. Similarity search
            similar_events = pinecone_client.similarity_search(embedding)

            # Verify multimodal workflow
            assert len(events) == 1
            assert events[0]["title"] == "Climate News"
            assert len(embedding) == 1536
            assert len(similar_events) == 0  # No duplicates found

            # Verify all clients were called
            mock_http_client.post.assert_called_once()
            mock_openai_instance.embeddings.create.assert_called_once()
            mock_index.query.assert_called_once()
