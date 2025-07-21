"""Audio generation service for creating news briefing podcasts from story summaries."""

from __future__ import annotations

from clients import MongoDBClient, OpenAIClient

from clients.cloudflare_r2 import CloudflareR2Client
from config.audio_config import (
    ANCHOR_SCRIPT_INSTRUCTIONS,
    ANCHOR_SCRIPT_MODEL,
    ANCHOR_SCRIPT_SYSTEM_PROMPT,
    AUDIO_FORMAT,
    TTS_MODEL,
    TTS_SPEED,
    TTS_VOICE,
)
from models import Podcast, Story
from utils import get_today_formatted, logger


def generate_podcast(
    stories: list[Story],
    *,
    openai_client: OpenAIClient,
    mongodb_client: MongoDBClient,
    r2_client: CloudflareR2Client,
) -> Podcast:
    """Generate a podcast from story summaries and store in Cloudflare R2 CDN.
    
    Args:
        stories: List of Story objects to include in the podcast
        openai_client: OpenAI client for script generation and TTS
        mongodb_client: MongoDB client for persisting podcast metadata
        r2_client: Cloudflare R2 client for CDN storage
        
    Returns:
        Generated Podcast object with CDN URL
    """
    if not stories:
        logger.warning("No stories provided for podcast generation")
        raise ValueError("Cannot generate podcast without stories")
    
    logger.info("🎙️ STEP 7: Audio Generation - Creating news briefing podcast...")
    
    # Step 1: Extract summaries from stories
    logger.info("  📝 Extracting summaries from %d stories...", len(stories))
    summaries = []
    for i, story in enumerate(stories, 1):
        summaries.append(f"Story {i}: {story.summary}")
    
    summaries_text = "\n\n".join(summaries)
    
    # Step 2: Generate anchor script using GPT-4o
    logger.info("  🎬 Generating anchor script with %s...", ANCHOR_SCRIPT_MODEL)
    
    user_prompt = ANCHOR_SCRIPT_INSTRUCTIONS.format(
        date=get_today_formatted(),
        story_count=len(stories),
        summaries=summaries_text,
    )
    
    full_prompt = f"{ANCHOR_SCRIPT_SYSTEM_PROMPT}\n\n{user_prompt}"
    
    anchor_script = openai_client.chat_completion(
        full_prompt,
        model=ANCHOR_SCRIPT_MODEL,
    )
    
    script_word_count = len(anchor_script.split())
    logger.info("  ✓ Anchor script generated: %d words", script_word_count)
    
    # Step 3: Convert script to speech using TTS
    logger.info("  🔊 Converting script to speech using %s...", TTS_MODEL)
    
    audio_bytes = openai_client.text_to_speech(
        anchor_script,
        model=TTS_MODEL,
        voice=TTS_VOICE,
        speed=TTS_SPEED,
        response_format=AUDIO_FORMAT,
    )
    
    file_size_bytes = len(audio_bytes)
    logger.info(
        "  ✓ Audio generated: %.1f MB",
        file_size_bytes / (1024 * 1024),
    )
    
    # Step 4: Upload to Cloudflare R2 CDN and store metadata
    logger.info("  ☁️ Uploading to Cloudflare R2 CDN...")
    cdn_url = r2_client.upload_audio(audio_bytes)
    
    # Step 5: Create Podcast object with CDN URL
    podcast = Podcast(
        anchor_script=anchor_script,
        audio_url=cdn_url,
        audio_size_bytes=file_size_bytes,
        story_count=len(stories),
    )
    
    # Step 6: Store podcast metadata in MongoDB
    logger.info("  💾 Saving podcast metadata to database...")
    podcast_dict = podcast.__dict__.copy()
    inserted_id = mongodb_client.insert_podcast(podcast_dict)
    logger.info("  ✓ Podcast saved with CDN URL (ID: %s)", inserted_id[:12] + "...")
    
    logger.info(
        "✅ Audio generation complete: %d-story podcast created",
        len(stories),
    )
    
    return podcast
