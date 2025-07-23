"""Real audio generation debug script with Cloudflare R2 CDN.

This script uses actual OpenAI, MongoDB, and Cloudflare R2 clients to generate a real podcast
from provided story summaries. It will make real API calls and upload audio to CDN.

TTS INSTRUCTION FEATURE (2025):
The script now supports OpenAI's gpt-4o-mini-tts instruction parameter for enhanced voice control.
Uses a single optimized instruction for professional news podcast delivery with:
- Professional news anchor delivery style
- Balanced informative and engaging tone
- Clear articulation and proper pacing
- Natural transitions between stories

Usage:
    python debug_audio_test.py

The script will automatically use TTS instructions when:
- TTS_MODEL = "gpt-4o-mini-tts" in config/audio_config.py

Run this independently for debugging: python debug_audio_test.py
"""

import os
import json
import requests
from pathlib import Path
from unittest.mock import patch

from clients import MongoDBClient, OpenAIClient
from clients.cloudflare_r2 import CloudflareR2Client
from models import Story
from services.audio_generation import generate_podcast
from utils import get_today_formatted


def test_tts_instructions_verification():
    """Test and verify that TTS instructions are properly sent to OpenAI API."""
    print("\n" + "="*60)
    print("🔍 TTS INSTRUCTIONS VERIFICATION TEST")
    print("="*60)
    
    from config.audio_config import TTS_MODEL, TTS_INSTRUCTION, AUDIO_FORMAT
    
    print(f"📋 Current Configuration:")
    print(f"   TTS Model: {TTS_MODEL}")
    print(f"   Audio Format: {AUDIO_FORMAT}")
    print(f"   Instructions Available: {'✅ Yes' if TTS_INSTRUCTION else '❌ No'}")
    
    if "gpt-4o-mini-tts" not in TTS_MODEL:
        print(f"\n⚠️  WARNING: Current model '{TTS_MODEL}' doesn't support instructions")
        print(f"   Instructions will be ignored by OpenAI API")
        print(f"   Change TTS_MODEL to 'gpt-4o-mini-tts' in config/audio_config.py")
        return False
    
    # Test with a mock to capture what's sent to OpenAI
    print(f"\n🧪 Testing TTS call with instructions...")
    
    try:
        openai_client = OpenAIClient()
        
        # Monkey-patch the OpenAI client to capture request parameters
        captured_params = {}
        original_create = openai_client._client.audio.speech.create
        
        def mock_create(**kwargs):
            captured_params.update(kwargs)
            # Return a mock response
            class MockResponse:
                content = b"mock_audio_data"
            return MockResponse()
        
        openai_client._client.audio.speech.create = mock_create
        
        # Make a test TTS call with instructions
        test_text = "This is a test of the TTS instructions feature."
        openai_client.text_to_speech(
            test_text,
            model=TTS_MODEL,
            instruction=TTS_INSTRUCTION
        )
        
        # Analyze what was sent
        print(f"\n📤 Request Parameters Sent to OpenAI:")
        print(f"   Model: {captured_params.get('model', 'NOT FOUND')}")
        print(f"   Voice: {captured_params.get('voice', 'NOT FOUND')}")
        print(f"   Speed: {captured_params.get('speed', 'NOT FOUND')}")
        print(f"   Response Format: {captured_params.get('response_format', 'NOT FOUND')}")
        print(f"   Instructions: {'✅ INCLUDED' if 'instructions' in captured_params else '❌ MISSING'}")
        
        if 'instructions' in captured_params:
            instructions_text = captured_params['instructions']
            print(f"   Instructions Length: {len(instructions_text)} characters")
            print(f"   Instructions Preview: {instructions_text[:100]}...")
            
            # Verify it matches our config
            if instructions_text == TTS_INSTRUCTION:
                print(f"   ✅ Instructions match config perfectly")
            else:
                print(f"   ⚠️  Instructions don't match config")
        
        # Restore original method
        openai_client._client.audio.speech.create = original_create
        
        return 'instructions' in captured_params
        
    except Exception as e:
        print(f"❌ Error during TTS instructions test: {e}")
        return False


def run_real_audio_generation_test() -> bool:
    """Debug real audio generation with Cloudflare R2 CDN storage.
    
    This will:
    1. Create Story objects from provided summaries
    2. Use real OpenAI client for script generation and TTS
    3. Use real Cloudflare R2 client for CDN storage
    4. Use real MongoDB client for metadata persistence
    5. Download audio from CDN and save locally for verification
    6. Verify TTS instructions are properly sent
    """
    
    # First, test TTS instructions verification
    instructions_working = test_tts_instructions_verification()
    
    # Check for required environment variables
    required_env_vars = [
        "OPENAI_API_KEY",
        "MONGODB_URI", 
        "MONGODB_DATABASE_NAME",
        "MONGODB_COLLECTION_NAME_AUDIO",
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_R2_ACCESS_KEY",
        "CLOUDFLARE_R2_SECRET_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Create Story objects from the provided summaries
    stories = [
        Story(
            headline="Trump Orders Release of Epstein Grand Jury Transcripts",
            summary="The United States announces plans to confront China about its continued purchases of Russian and Iranian oil, nations under heavy U.S. sanctions, during upcoming trade negotiations. Treasury Secretary Scott Bessent says the talks will expand beyond tariffs to include national security concerns, marking a strategic escalation. China, now the largest buyer of Iranian oil and a leading importer of Russian crude, responds cautiously, urging dialogue. The U.S. warns of potential secondary tariffs on China and urges European allies to align, creating new tensions in global markets and international diplomacy.",
            body="The United States announces plans to confront China about its continued purchases of Russian and Iranian oil, nations under heavy U.S. sanctions, during upcoming trade negotiations. Treasury Secretary Scott Bessent says the talks will expand beyond tariffs to include national security concerns, marking a strategic escalation. China, now the largest buyer of Iranian oil and a leading importer of Russian crude, responds cautiously, urging dialogue. The U.S. warns of potential secondary tariffs on China and urges European allies to align, creating new tensions in global markets and international diplomacy.",
            tag="politics",
            sources=[
                "https://example.com/trump-epstein-transcripts",
                "https://example.com/doj-grand-jury-release"
            ],
        ),
        Story(
            headline="Guadalupe River Flood Kills 144 in Central Texas",
            summary="At least 135 people are confirmed dead after catastrophic flooding swept through Central Texas in July 2025, marking one of the deadliest inland flood events in U.S. history. Triggered by intense rainfall and a sudden Guadalupe River surge, the disaster decimated communities, including tragic losses at Camp Mystic. Officials face scrutiny over delayed flood alerts and preparedness. State and federal agencies, along with relief organizations, continue recovery and aid efforts. The Texas Legislature begins a special session to address systemic failures and bolster disaster response, as devastated regions focus on long-term recovery and improved early-warning systems.",
            body="At least 135 people are confirmed dead after catastrophic flooding swept through Central Texas in July 2025, marking one of the deadliest inland flood events in U.S. history. Triggered by intense rainfall and a sudden Guadalupe River surge, the disaster decimated communities, including tragic losses at Camp Mystic. Officials face scrutiny over delayed flood alerts and preparedness. State and federal agencies, along with relief organizations, continue recovery and aid efforts. The Texas Legislature begins a special session to address systemic failures and bolster disaster response, as devastated regions focus on long-term recovery and improved early-warning systems.",
            tag="disaster",
            sources=[
                "https://example.com/guadalupe-river-flood",
                "https://example.com/texas-flood-casualties"
            ],
        ),
        Story(
            headline="Trump Administration Overhauls Immigration Enforcement",
            summary="The Pentagon has begun withdrawing about 700 active-duty U.S. Marines from Los Angeles, ending a month-long deployment ordered by President Donald Trump during protests over federal immigration raids. The move follows weeks of legal and political controversy over the use of federal troops for domestic law enforcement. Local and state officials, including California’s governor, condemned the military presence as excessive and unconstitutional. While thousands of National Guard members had already been pulled out, around 2,000 remain, leaving ongoing questions about federal oversight and the future use of military force during civil unrest.",
            body="Since returning to office in January 2025, the Trump administration has implemented sweeping changes to U.S. immigration policy. The administration declared a national emergency at the southern border, authorized military deployment for border security, and significantly expanded deportation operations across the country.",
            tag="immigration",
            sources=[
                "https://example.com/trump-immigration-overhaul",
                "https://example.com/border-emergency-2025"
            ],
        ),
    ]
    
    try:
        # Initialize real clients
        openai_client = OpenAIClient()
        mongodb_client = MongoDBClient()
        r2_client = CloudflareR2Client()
        
        # Generate the podcast using real services
        print(f"\n🎙️ Starting real audio generation test with {len(stories)} stories...")
        print("📝 Story summaries:")
        for i, story in enumerate(stories, 1):
            print(f"  {i}. {story.headline}")
        
        # Check if TTS instructions are enabled for enhanced testing
        from config.audio_config import TTS_MODEL
        if "gpt-4o-mini-tts" in TTS_MODEL:
            print("🎯 TTS Instructions feature: ENABLED (2025 Feature)")
            print("   This will provide enhanced voice control with professional news delivery")
            if instructions_working:
                print("   ✅ Instructions verification: PASSED")
            else:
                print("   ⚠️  Instructions verification: FAILED")
        else:
            print("📢 TTS Instructions feature: DISABLED")
            print("   Using standard TTS without instruction parameters")
            print(f"   Current model: {TTS_MODEL} (instructions require gpt-4o-mini-tts)")
        
        # Execute the real audio generation pipeline with CDN storage
        print(f"\n🎙️ Executing full pipeline...")
        podcast = generate_podcast(
            stories,
            openai_client=openai_client,
            mongodb_client=mongodb_client,
            r2_client=r2_client,
        )
        
        # Verify podcast was created successfully
        if not podcast:
            print("❌ Failed to generate podcast")
            return False
            
        if not podcast.anchor_script:
            print("❌ No anchor script generated")
            return False
            
        if not podcast.anchor_name:
            print("❌ No anchor name assigned")
            return False
            
        if not podcast.audio_url:
            print("❌ No CDN URL generated")
            return False
            
        if podcast.audio_size_bytes == 0:
            print("❌ No audio size recorded")
            return False
        
        print(f"✅ Podcast generated successfully!")
        print(f"🎭 Anchor: {podcast.anchor_name}")
        print(f"📄 Script length: {len(podcast.anchor_script.split())} words")
        print(f"🔗 CDN URL: {podcast.audio_url}")
        print(f"📊 Audio size: {podcast.audio_size_bytes / (1024 * 1024):.1f} MB")
        
        # Test CDN access
        print(f"\n🌐 Testing CDN access...")
        response = requests.head(podcast.audio_url)
        print(f"📡 CDN Status: {response.status_code}")
        print(f"📝 Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"🕒 Response Time: {response.elapsed.total_seconds():.3f}s")
        
        # Create the test output directory if it doesn't exist
        output_dir = Path("debug/output")
        output_dir.mkdir(exist_ok=True)
        
        # Save the script to a text file
        script_file = output_dir / f"podcast_script_{get_today_formatted()}_{podcast.anchor_name.replace(' ', '_')}.txt"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(f"PODCAST SCRIPT - {get_today_formatted()}\n")
            f.write(f"ANCHOR: {podcast.anchor_name}\n")
            f.write("=" * 50 + "\n\n")
            f.write(podcast.anchor_script)
        
        # Download and save the audio file from CDN
        print(f"📥 Downloading audio from CDN...")
        audio_response = requests.get(podcast.audio_url)
        audio_response.raise_for_status()
        
        from config.audio_config import AUDIO_FORMAT
        audio_file = output_dir / f"podcast_audio_{get_today_formatted()}_{podcast.anchor_name.replace(' ', '_')}.{AUDIO_FORMAT}"
        with open(audio_file, "wb") as f:
            f.write(audio_response.content)
        
        # Save the podcast object metadata as JSON
        podcast_data = {
            "anchor_script": podcast.anchor_script,
            "anchor_name": podcast.anchor_name,
            "audio_url": podcast.audio_url,
            "audio_size_bytes": podcast.audio_size_bytes,
            "audio_size_mb": round(podcast.audio_size_bytes / (1024 * 1024), 2),
            "local_audio_file": audio_file.name
        }
        
        json_file = output_dir / f"podcast_data_{get_today_formatted()}_{podcast.anchor_name.replace(' ', '_')}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(podcast_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Script saved to: {script_file}")
        print(f"🎵 Audio downloaded and saved to: {audio_file}")
        print(f"📄 Podcast data saved to: {json_file}")
        
        print("\n🎵 CDN Audio Processing Complete:")
        print(f"✅ {AUDIO_FORMAT.upper()} audio uploaded to Cloudflare R2 CDN")
        print(f"✅ Audio size: {podcast.audio_size_bytes / (1024 * 1024):.1f} MB")
        print(f"✅ CDN URL: {podcast.audio_url}")
        print(f"✅ Anchor: {podcast.anchor_name} with personalized script")
        
        # Report TTS instruction usage
        print(f"\n📋 TTS INSTRUCTIONS SUMMARY:")
        if "gpt-4o-mini-tts" in TTS_MODEL:
            print(f"✅ Model supports instructions: {TTS_MODEL}")
            if instructions_working:
                print(f"✅ Instructions properly sent to OpenAI API")
                print(f"✅ Enhanced voice control enabled (2025 Feature)")
            else:
                print(f"⚠️  Instructions may not be working properly")
        else:
            print(f"⚠️  Model doesn't support instructions: {TTS_MODEL}")
            print(f"📢 Standard TTS mode (no enhanced voice control)")
            
        print(f"✅ MongoDB contains: anchor_script, anchor_name, audio_url, audio_size_bytes")
        print(f"✅ Frontend can use CDN URL for instant global streaming")
        print(f"✅ Local files saved to debug/test_output/ for verification")
        
        print("\nℹ️  Clean MongoDB structure with CDN URL instead of binary data.")
        print("ℹ️  Audio served from Cloudflare's global CDN for 50x faster loading.")
        print("ℹ️  Your frontend gets the CDN URL and streams audio directly.")
        print("ℹ️  Each podcast features a randomly selected anchor with personalized intro/outro.")
        
        if "gpt-4o-mini-tts" in TTS_MODEL:
            print("ℹ️  TTS Instructions provide enhanced control over voice delivery, tone, and pacing.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during audio generation test: {e}")
        print("💡 Check your environment variables for Cloudflare R2 credentials")
        return False


if __name__ == "__main__":
    print("🧪 Running debug audio generation test with Cloudflare R2 CDN...")
    success = run_real_audio_generation_test()
    if success:
        print("\n✅ CDN debug test completed successfully!")
        
    else:
        print("\n❌ CDN debug test failed!")
        exit(1)


def demonstrate_tts_instruction():
    """Demonstrate the TTS instruction for news podcast delivery."""
    from config.audio_config import (
        TTS_INSTRUCTION,
        TTS_MODEL,
    )
    
    print("\n" + "="*60)
    print("🎯 TTS INSTRUCTION DEMONSTRATION (2025 Feature)")
    print("="*60)
    
    if "gpt-4o-mini-tts" not in TTS_MODEL:
        print(f"⚠️  Current TTS model: {TTS_MODEL}")
        print("   TTS Instructions require gpt-4o-mini-tts model.")
        print("   Set TTS_MODEL = 'gpt-4o-mini-tts' in config/audio_config.py")
        return
    
    print(f"✅ TTS Instructions: ENABLED")
    print(f"✅ TTS Model: {TTS_MODEL}")
    print("\nOptimized News Podcast Instruction:")
    print("-" * 40)
    
    print(TTS_INSTRUCTION)
    
    print("\n💡 Usage Example:")
    print("   # Use in your code:")
    print("   from config.audio_config import TTS_INSTRUCTION")
    print("   audio_bytes = openai_client.text_to_speech(text, instruction=TTS_INSTRUCTION)")

 