"""Audio generation service for creating news briefing podcasts from story summaries."""

from __future__ import annotations

from clients import MongoDBClient, OpenAIClient

from clients.cloudflare_r2 import CloudflareR2Client
from config.audio_config import (
    ANCHOR_SCRIPT_INSTRUCTIONS,
    ANCHOR_SCRIPT_MODEL,
    ANCHOR_SCRIPT_SYSTEM_PROMPT,
    AUDIO_FORMAT,
    TTS_INSTRUCTION,
    TTS_MODEL,
    TTS_SPEED,
    get_random_anchor,
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
    
    # Step 1: Select random anchor for this podcast
    tts_voice, anchor_name = get_random_anchor()
    logger.info("  🎭 Selected anchor: %s (voice: %s)", anchor_name, tts_voice)
    
    # Step 2: Extract summaries from stories
    logger.info("  📝 Extracting summaries from %d stories...", len(stories))
    summaries = []
    for i, story in enumerate(stories, 1):
        summaries.append(f"Story {i}: {story.summary}")
    
    summaries_text = "\n\n".join(summaries)
    
    # Step 3: Generate anchor script using GPT-4o
    logger.info("  🎬 Generating anchor script with %s...", ANCHOR_SCRIPT_MODEL)
    
    user_prompt = ANCHOR_SCRIPT_INSTRUCTIONS.format(
        date=get_today_formatted(),
        anchor_name=anchor_name,
        summaries=summaries_text,
    )
    
    anchor_script = openai_client.chat_completion(
        user_prompt,
        model=ANCHOR_SCRIPT_MODEL,
        system_prompt=ANCHOR_SCRIPT_SYSTEM_PROMPT,
    )
    
    script_word_count = len(anchor_script.split())
    logger.info("  ✓ Anchor script generated: %d words", script_word_count)
    
    # Step 4: Convert script to speech using TTS
    logger.info("  🔊 Converting script to speech using %s...", TTS_MODEL)
    
    # Get TTS instruction for enhanced voice control (2025 feature)
    tts_instruction = None
    if "gpt-4o-mini-tts" in TTS_MODEL:
        tts_instruction = TTS_INSTRUCTION
        logger.info("  🎯 Using TTS instructions for enhanced voice control")
    
    audio_bytes = openai_client.text_to_speech(
        anchor_script,
        model=TTS_MODEL,
        voice=tts_voice,
        speed=TTS_SPEED,
        response_format=AUDIO_FORMAT,
        instruction=tts_instruction,
    )
    
    file_size_bytes = len(audio_bytes)
    logger.info(
        "  ✓ Audio generated: %.1f MB",
        file_size_bytes / (1024 * 1024),
    )
    
    # Step 5: Upload to Cloudflare R2 CDN and store metadata
    logger.info("  ☁️ Uploading to Cloudflare R2 CDN...")
    cdn_url = r2_client.upload_audio(audio_bytes)
    
    # Step 6: Create Podcast object with CDN URL
    podcast = Podcast(
        anchor_script=anchor_script,
        anchor_name=anchor_name,
        audio_url=cdn_url,
        audio_size_bytes=file_size_bytes,
    )
    
    # Step 7: Store podcast metadata in MongoDB
    logger.info("  💾 Saving podcast metadata to database...")
    podcast_dict = podcast.__dict__.copy()
    inserted_id = mongodb_client.insert_podcast(podcast_dict)
    logger.info("  ✓ Podcast saved with CDN URL (ID: %s)", inserted_id[:12] + "...")
    
    logger.info(
        "✅ Audio generation complete: %d-story podcast created by %s",
        len(stories),
        anchor_name,
    )
    
    return podcast
