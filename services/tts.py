from __future__ import annotations

from typing import List

from clients import OpenAIClient
from config import TTS_INSTRUCTIONS
from config.settings import CHAT_MODEL
from utils import logger, Article, get_random_REPORTER_VOICE


def generate_broadcast_analysis(
    articles: List[Article], 
    *, 
    openai_client: OpenAIClient
) -> List[Article]:
    """
    Generate TTS analysis for articles with broadcast and reporter fields.
    
    This service:
    1. Takes research articles as input
    2. Generates reporter analysis using CHAT_MODEL
    3. Converts analysis to MP3 using TTS_MODEL with random reporter voice
    4. Adds MP3 data as "broadcast" field
    5. Adds human name as "reporter" field
    
    Args:
        articles: List of articles from research service
        openai_client: OpenAI client for chat and TTS
        
    Returns:
        List of articles with broadcast and reporter fields populated
    """
    processed_articles: List[Article] = []
    
    for article in articles:
        try:
            # Generate reporter analysis using CHAT_MODEL
            analysis_prompt = TTS_INSTRUCTIONS.format(
                headline=article.headline,
                summary=article.summary,
                story=article.story
            )
            
            logger.info("Generating analysis for: '%s'", article.headline)
            analysis_text = openai_client.chat_completion(analysis_prompt, model=CHAT_MODEL)
            
            # Get random reporter voice
            voice_api_name, voice_human_name = get_random_REPORTER_VOICE()
            logger.info("Selected reporter: %s (%s)", voice_human_name, voice_api_name)
            
            # Convert analysis to speech using TTS_MODEL
            logger.info("Converting to speech: '%s'", article.headline)
            mp3_data = openai_client.text_to_speech(analysis_text, voice_api_name)
            
            # Create new article with broadcast data and reporter info
            article_with_broadcast = Article(
                headline=article.headline,
                summary=article.summary,
                story=article.story,
                sources=article.sources,
                broadcast=mp3_data,
                reporter=voice_human_name
            )
            
            logger.info(
                "Generated broadcast for: '%s' (reporter=%s, %d bytes)", 
                article_with_broadcast.headline, 
                voice_human_name,
                len(mp3_data)
            )
            
            processed_articles.append(article_with_broadcast)
            
        except Exception as e:
            logger.error("Failed to process article '%s': %s", article.headline, str(e))
            # Since broadcast and reporter are now required fields, we cannot create
            # an Article without them. In case of failure, we skip this article.
            # In a production environment, you might want to implement fallback logic
            # such as generating a default TTS message or retrying with different parameters.
            continue
    
    logger.info("Generated broadcasts: %d/%d articles processed", 
                len(processed_articles), 
                len(articles))
    
    return processed_articles
