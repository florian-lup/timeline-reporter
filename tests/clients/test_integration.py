"""Integration tests for client interactions."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from clients import MongoDBClient, OpenAIClient, PerplexityClient, PineconeClient
from utils import Article


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

    def test_complete_tts_workflow(self):
        """Test complete workflow including TTS generation and storage."""
        with patch('clients.openai.OpenAI') as mock_openai:
            with patch('clients.mongodb.MongoClient') as mock_mongo:
                with patch('services.tts.get_random_REPORTER_VOICE', return_value=('ash', 'Alex')):
                    # Setup OpenAI mock for both chat and TTS
                    mock_openai_instance = Mock()
                    mock_openai.return_value = mock_openai_instance
                    
                    # Mock chat completion for analysis generation
                    mock_chat_response = Mock()
                    mock_choice = Mock()
                    mock_message = Mock()
                    mock_message.content = "This is an engaging analysis of the AI breakthrough for broadcast presentation."
                    mock_choice.message = mock_message
                    mock_chat_response.choices = [mock_choice]
                    mock_openai_instance.chat.completions.create.return_value = mock_chat_response
                    
                    # Mock TTS response
                    mock_tts_response = Mock()
                    mock_tts_response.content = b"fake_mp3_audio_data_for_broadcast"
                    mock_openai_instance.audio.speech.create.return_value = mock_tts_response
                    
                    # Setup MongoDB mock
                    mock_mongo_instance = Mock()
                    mock_mongo.return_value = mock_mongo_instance
                    mock_db = Mock()
                    mock_collection = Mock()
                    mock_mongo_instance.__getitem__ = Mock(return_value=mock_db)
                    mock_db.__getitem__ = Mock(return_value=mock_collection)
                    mock_result = Mock()
                    mock_result.inserted_id = "507f1f77bcf86cd799439012"
                    mock_collection.insert_one.return_value = mock_result
                    
                    # Execute TTS workflow
                    from services import generate_broadcast_analysis
                    
                    openai_client = OpenAIClient()
                    mongodb_client = MongoDBClient()
                    
                    # Create test article with required fields
                    test_articles = [
                        Article(
                            headline="AI Breakthrough in 2024",
                            summary="Revolutionary AI model shows unprecedented capabilities",
                            story="Detailed story about the groundbreaking AI development...",
                            sources=["https://example.com/ai-news"],
                            broadcast=b"",  # Placeholder
                            reporter=""     # Placeholder
                        )
                    ]
                    
                    # Run TTS service
                    result_articles = generate_broadcast_analysis(
                        test_articles,
                        openai_client=openai_client,
                        mongodb_client=mongodb_client
                    )
                    
                    # Verify results
                    assert len(result_articles) == 1
                    processed_article = result_articles[0]
                    
                    # Check TTS output
                    assert processed_article.broadcast == b"fake_mp3_audio_data_for_broadcast"
                    assert processed_article.reporter == "Alex"
                    assert processed_article.headline == "AI Breakthrough in 2024"
                    
                    # Verify OpenAI calls
                    mock_openai_instance.chat.completions.create.assert_called_once()
                    mock_openai_instance.audio.speech.create.assert_called_once()
                    
                    # Verify TTS parameters
                    tts_call = mock_openai_instance.audio.speech.create.call_args
                    assert tts_call[1]['voice'] == 'ash'
                    assert tts_call[1]['input'] == "This is an engaging analysis of the AI breakthrough for broadcast presentation."
                    assert tts_call[1]['response_format'] == 'mp3'
                    
                    # Verify MongoDB storage
                    mock_collection.insert_one.assert_called_once()
                    stored_data = mock_collection.insert_one.call_args[0][0]
                    assert stored_data['broadcast'] == b"fake_mp3_audio_data_for_broadcast"
                    assert stored_data['reporter'] == "Alex"

    def test_openai_chat_and_tts_integration(self):
        """Test integration of OpenAI chat completion and TTS functionality."""
        with patch('clients.openai.OpenAI') as mock_openai:
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            
            # Mock chat completion
            mock_chat_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Generated analysis text for TTS conversion"
            mock_choice.message = mock_message
            mock_chat_response.choices = [mock_choice]
            mock_openai_instance.chat.completions.create.return_value = mock_chat_response
            
            # Mock TTS
            mock_tts_response = Mock()
            mock_tts_response.content = b"converted_audio_data"
            mock_openai_instance.audio.speech.create.return_value = mock_tts_response
            
            with patch('clients.openai.OPENAI_API_KEY', 'test-api-key'):
                client = OpenAIClient()
                
                # 1. Generate analysis text
                analysis_text = client.chat_completion("Create analysis for: AI breakthrough news", model="test-model")
                
                # 2. Convert to speech
                audio_data = client.text_to_speech(analysis_text, "alloy")
                
                # Verify integration
                assert analysis_text == "Generated analysis text for TTS conversion"
                assert audio_data == b"converted_audio_data"
                
                # Verify method calls
                mock_openai_instance.chat.completions.create.assert_called_once()
                mock_openai_instance.audio.speech.create.assert_called_once()
                
                # Verify the text from chat is used in TTS
                tts_call = mock_openai_instance.audio.speech.create.call_args
                assert tts_call[1]['input'] == analysis_text

    def test_article_model_with_required_fields(self):
        """Test Article model integration with required broadcast and reporter fields."""
        # Test creating Article with all required fields
        article = Article(
            headline="Test Headline",
            summary="Test summary",
            story="Test story content",
            sources=["https://example.com"],
            broadcast=b"audio_data",
            reporter="Alex"
        )
        
        assert article.headline == "Test Headline"
        assert article.broadcast == b"audio_data"
        assert article.reporter == "Alex"
        
        # Test converting to dict for MongoDB storage
        article_dict = article.__dict__
        expected_keys = {'headline', 'summary', 'story', 'sources', 'broadcast', 'reporter'}
        assert set(article_dict.keys()) == expected_keys
        
        # Test that all fields are present (no None values)
        for key, value in article_dict.items():
            assert value is not None, f"Field {key} should not be None"

    def test_research_to_tts_pipeline_integration(self):
        """Test integration from research service through TTS to storage."""
        with patch('clients.perplexity.httpx.Client') as mock_httpx:
            with patch('clients.openai.OpenAI') as mock_openai:
                with patch('clients.mongodb.MongoClient') as mock_mongo:
                    with patch('services.tts.get_random_REPORTER_VOICE', return_value=('ballad', 'Blake')):
                        # Setup Perplexity mock (research)
                        mock_http_client = Mock()
                        mock_response = Mock()
                        article_data = {
                            "headline": "Breaking News",
                            "summary": "Important event summary",
                            "story": "Full story details...",
                            "sources": ["https://source.com"]
                        }
                        mock_response.json.return_value = {
                            "choices": [{"message": {"content": json.dumps(article_data)}}]
                        }
                        mock_response.raise_for_status.return_value = None
                        mock_httpx.return_value.__enter__.return_value = mock_http_client
                        mock_http_client.post.return_value = mock_response
                        
                        # Setup OpenAI mock (chat + TTS)
                        mock_openai_instance = Mock()
                        mock_openai.return_value = mock_openai_instance
                        
                        # Chat completion for analysis
                        mock_chat_response = Mock()
                        mock_choice = Mock()
                        mock_message = Mock()
                        mock_message.content = "Professional analysis of the breaking news for broadcast."
                        mock_choice.message = mock_message
                        mock_chat_response.choices = [mock_choice]
                        mock_openai_instance.chat.completions.create.return_value = mock_chat_response
                        
                        # TTS conversion
                        mock_tts_response = Mock()
                        mock_tts_response.content = b"broadcast_audio_data"
                        mock_openai_instance.audio.speech.create.return_value = mock_tts_response
                        
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
                        from services import research_events, generate_broadcast_analysis
                        from utils import Event
                        
                        perplexity_client = PerplexityClient()
                        openai_client = OpenAIClient()
                        mongodb_client = MongoDBClient()
                        
                        # 1. Research phase
                        test_events = [Event(title="Breaking News", summary="Important event")]
                        articles = research_events(test_events, perplexity_client=perplexity_client)
                        
                        # 2. TTS phase
                        final_articles = generate_broadcast_analysis(
                            articles,
                            openai_client=openai_client,
                            mongodb_client=mongodb_client
                        )
                        
                        # Verify end-to-end pipeline
                        assert len(final_articles) == 1
                        final_article = final_articles[0]
                        
                        # Check research data is preserved
                        assert final_article.headline == "Breaking News"
                        assert final_article.summary == "Important event summary"
                        assert final_article.story == "Full story details..."
                        assert final_article.sources == ["https://source.com"]
                        
                        # Check TTS data is added
                        assert final_article.broadcast == b"broadcast_audio_data"
                        assert final_article.reporter == "Blake"
                        
                        # Verify all services were called
                        mock_http_client.post.assert_called_once()  # Perplexity research
                        mock_openai_instance.chat.completions.create.assert_called_once()  # Analysis generation
                        mock_openai_instance.audio.speech.create.assert_called_once()  # TTS conversion
                        mock_collection.insert_one.assert_called_once()  # MongoDB storage

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

    @pytest.mark.slow 
    def test_tts_error_handling_integration(self):
        """Test error handling in TTS workflow integration."""
        with patch('clients.openai.OpenAI') as mock_openai:
            with patch('clients.mongodb.MongoClient') as mock_mongo:
                # Setup OpenAI mock to fail on TTS
                mock_openai_instance = Mock()
                mock_openai.return_value = mock_openai_instance
                
                # Chat completion succeeds
                mock_chat_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = "Analysis text"
                mock_choice.message = mock_message
                mock_chat_response.choices = [mock_choice]
                mock_openai_instance.chat.completions.create.return_value = mock_chat_response
                
                # TTS fails
                mock_openai_instance.audio.speech.create.side_effect = Exception("TTS API Error")
                
                # MongoDB setup (shouldn't be called due to TTS failure)
                mock_mongo_instance = Mock()
                mock_mongo.return_value = mock_mongo_instance
                mock_db = Mock()
                mock_collection = Mock()
                mock_mongo_instance.__getitem__ = Mock(return_value=mock_db)
                mock_db.__getitem__ = Mock(return_value=mock_collection)
                
                from services import generate_broadcast_analysis
                
                openai_client = OpenAIClient()
                mongodb_client = MongoDBClient()
                
                test_articles = [
                    Article(
                        headline="Test",
                        summary="Test",
                        story="Test",
                        sources=[],
                        broadcast=b"",
                        reporter=""
                    )
                ]
                
                # Should handle error gracefully and return empty list
                result = generate_broadcast_analysis(
                    test_articles,
                    openai_client=openai_client,
                    mongodb_client=mongodb_client
                )
                
                assert len(result) == 0  # Article skipped due to TTS failure
                mock_collection.insert_one.assert_not_called()  # No storage due to failure 