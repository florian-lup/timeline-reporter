"""Integration tests for client interactions."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from clients.mongodb import MongoDBClient
from clients.openai import OpenAIClient
from clients.perplexity import PerplexityClient
from clients.pinecone import PineconeClient


@pytest.mark.integration
class TestClientIntegration:
    """Integration tests showing how clients work together."""

    def test_research_to_storage_workflow(self):
        """Test complete workflow from research to storage."""
        # Mock all external dependencies
        with patch('clients.perplexity.httpx.Client') as mock_httpx:
            with patch('clients.openai.OpenAI') as mock_openai:
                with patch('clients.mongodb.MongoClient') as mock_mongo:
                    with patch('clients.pinecone.Pinecone') as mock_pinecone:
                        # Setup Perplexity mock
                        mock_http_client = Mock()
                        mock_response = Mock()
                        article_data = {
                            "headline": "AI Breakthrough",
                            "summary": "New AI model shows remarkable capabilities",
                            "story": "Detailed story about AI breakthrough...",
                            "sources": ["https://example.com/ai-news"]
                        }
                        mock_response.json.return_value = {
                            "choices": [{"message": {"content": json.dumps(article_data)}}]
                        }
                        mock_response.raise_for_status.return_value = None
                        mock_httpx.return_value.__enter__.return_value = mock_http_client
                        mock_http_client.post.return_value = mock_response
                        
                        # Setup OpenAI mock
                        mock_openai_instance = Mock()
                        mock_openai.return_value = mock_openai_instance
                        mock_embed_response = Mock()
                        mock_embed_data = Mock()
                        mock_embed_data.embedding = [0.1] * 1536
                        mock_embed_response.data = [mock_embed_data]
                        mock_openai_instance.embeddings.create.return_value = mock_embed_response
                        
                        # Setup MongoDB mock (fixed mocking)
                        mock_mongo_instance = Mock()
                        mock_mongo.return_value = mock_mongo_instance
                        mock_db = Mock()
                        mock_collection = Mock()
                        mock_mongo_instance.__getitem__ = Mock(return_value=mock_db)
                        mock_db.__getitem__ = Mock(return_value=mock_collection)
                        mock_result = Mock()
                        mock_result.inserted_id = "507f1f77bcf86cd799439011"
                        mock_collection.insert_one.return_value = mock_result
                        
                        # Setup Pinecone mock
                        mock_pinecone_instance = Mock()
                        mock_pinecone.return_value = mock_pinecone_instance
                        mock_pinecone_instance.list_indexes.return_value.names.return_value = ['timeline-events']
                        mock_index = Mock()
                        mock_pinecone_instance.Index.return_value = mock_index
                        
                        # Execute workflow
                        perplexity_client = PerplexityClient()
                        openai_client = OpenAIClient()
                        mongodb_client = MongoDBClient()
                        pinecone_client = PineconeClient()
                        
                        # 1. Research with Perplexity
                        research_result = perplexity_client.research("AI developments")
                        article = json.loads(research_result)
                        
                        # 2. Create embedding with OpenAI
                        text_to_embed = f"{article['headline']} {article['summary']}"
                        embedding = openai_client.embed_text(text_to_embed)
                        
                        # 3. Store in MongoDB
                        article_id = mongodb_client.insert_article(article)
                        
                        # 4. Store vector in Pinecone
                        pinecone_client.upsert_vector(article_id, embedding, {
                            "headline": article['headline'],
                            "date": "2024-01-01"
                        })
                        
                        # Verify the workflow
                        assert article['headline'] == "AI Breakthrough"
                        assert len(embedding) == 1536
                        assert article_id == "507f1f77bcf86cd799439011"
                        
                        # Verify all clients were called correctly
                        mock_http_client.post.assert_called_once()
                        mock_openai_instance.embeddings.create.assert_called_once()
                        mock_collection.insert_one.assert_called_once_with(article)
                        mock_index.upsert.assert_called_once()

    def test_similarity_search_workflow(self):
        """Test workflow for finding similar articles."""
        with patch('clients.openai.OpenAI') as mock_openai:
            with patch('clients.pinecone.Pinecone') as mock_pinecone:
                with patch('clients.mongodb.MongoClient') as mock_mongo:
                    # Setup mocks
                    mock_openai_instance = Mock()
                    mock_openai.return_value = mock_openai_instance
                    mock_embed_response = Mock()
                    mock_embed_data = Mock()
                    query_vector = [0.2] * 1536
                    mock_embed_data.embedding = query_vector
                    mock_embed_response.data = [mock_embed_data]
                    mock_openai_instance.embeddings.create.return_value = mock_embed_response
                    
                    mock_pinecone_instance = Mock()
                    mock_pinecone.return_value = mock_pinecone_instance
                    mock_pinecone_instance.list_indexes.return_value.names.return_value = ['timeline-events']
                    mock_index = Mock()
                    mock_pinecone_instance.Index.return_value = mock_index
                    
                    # Mock similarity search results
                    mock_match = Mock()
                    mock_match.id = "507f1f77bcf86cd799439011"
                    mock_match.score = 0.95
                    mock_query_result = Mock()
                    mock_query_result.matches = [mock_match]
                    mock_index.query.return_value = mock_query_result
                    
                    # Execute similarity search workflow
                    openai_client = OpenAIClient()
                    pinecone_client = PineconeClient()
                    
                    # 1. Create embedding for search query
                    query_embedding = openai_client.embed_text("machine learning news")
                    
                    # 2. Search for similar vectors
                    similar_results = pinecone_client.similarity_search(query_embedding)
                    
                    # Verify results
                    assert len(similar_results) == 1
                    assert similar_results[0][0] == "507f1f77bcf86cd799439011"
                    assert similar_results[0][1] == 0.95
                    
                    # Verify calls
                    mock_openai_instance.embeddings.create.assert_called_once()
                    mock_index.query.assert_called_once()

    @pytest.mark.slow
    def test_error_handling_in_workflow(self):
        """Test error handling across the workflow."""
        with patch('clients.perplexity.httpx.Client') as mock_httpx:
            # Setup failing HTTP request
            mock_http_client = Mock()
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("API Error")
            mock_httpx.return_value.__enter__.return_value = mock_http_client
            mock_http_client.post.return_value = mock_response
            
            perplexity_client = PerplexityClient()
            
            # Verify error propagation
            with pytest.raises(Exception, match="API Error"):
                perplexity_client.research("test query") 