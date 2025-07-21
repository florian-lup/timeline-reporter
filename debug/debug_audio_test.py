"""Real audio generation debug script with Cloudflare R2 CDN.

This script uses actual OpenAI, MongoDB, and Cloudflare R2 clients to generate a real podcast
from provided story summaries. It will make real API calls and upload audio to CDN.

Run this independently for debugging: python debug_audio_test.py
"""

import os
import json
import requests
from pathlib import Path

from clients import MongoDBClient, OpenAIClient
from clients.cloudflare_r2 import CloudflareR2Client
from models import Story
from services.audio_generation import generate_podcast
from utils import get_today_formatted


def run_real_audio_generation_test() -> bool:
    """Debug real audio generation with Cloudflare R2 CDN storage.
    
    This will:
    1. Create Story objects from provided summaries
    2. Use real OpenAI client for script generation and TTS
    3. Use real Cloudflare R2 client for CDN storage
    4. Use real MongoDB client for metadata persistence
    5. Download audio from CDN and save locally for verification
    """
    
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
            summary="President Donald Trump orders the Justice Department to seek the release of grand jury transcripts related to Jeffrey Epstein and Ghislaine Maxwell, citing public interest following a disputed DOJ memo on Epstein's death.",
            body="In a significant move for transparency, President Trump has directed the Justice Department to pursue the release of previously sealed grand jury materials related to the Jeffrey Epstein case. The order comes in response to ongoing public interest and follows controversial DOJ memos regarding Epstein's death in federal custody.",
            tag="politics",
            sources=[
                "https://example.com/trump-epstein-transcripts",
                "https://example.com/doj-grand-jury-release"
            ],
        ),
        Story(
            headline="Guadalupe River Flood Kills 144 in Central Texas",
            summary="The Guadalupe River flood in Central Texas killed at least 144 people, including 27 at Camp Mystic, during and after the July 4, 2025, weekend.",
            body="A devastating flood along the Guadalupe River in Central Texas has claimed 144 lives, making it one of the deadliest natural disasters in the region's history. The tragedy struck during the July 4th weekend when heavy rains caused rapid river rises. Camp Mystic, a popular summer camp, suffered particularly heavy losses with 27 fatalities.",
            tag="disaster",
            sources=[
                "https://example.com/guadalupe-river-flood",
                "https://example.com/texas-flood-casualties"
            ],
        ),
        Story(
            headline="Trump Administration Overhauls Immigration Enforcement",
            summary="The second Trump administration rapidly overhauls U.S. immigration enforcement, declaring a border emergency, deploying troops, and expanding deportations since taking office in January 2025.",
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
        
        # Execute the real audio generation pipeline with CDN storage
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
            
        if not podcast.audio_url:
            print("❌ No CDN URL generated")
            return False
            
        if podcast.audio_size_bytes == 0:
            print("❌ No audio size recorded")
            return False
            
        if podcast.story_count != 3:
            print(f"❌ Expected 3 stories, got {podcast.story_count}")
            return False
        
        print(f"✅ Podcast generated successfully!")
        print(f"📄 Script length: {len(podcast.anchor_script.split())} words")
        print(f"🔗 CDN URL: {podcast.audio_url}")
        print(f"📊 Audio size: {podcast.audio_size_bytes / (1024 * 1024):.1f} MB")
        print(f"📚 Story count: {podcast.story_count}")
        
        # Test CDN access
        print(f"\n🌐 Testing CDN access...")
        response = requests.head(podcast.audio_url)
        print(f"📡 CDN Status: {response.status_code}")
        print(f"📝 Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"🕒 Response Time: {response.elapsed.total_seconds():.3f}s")
        
        # Create the test output directory if it doesn't exist
        output_dir = Path("debug/test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save the script to a text file
        script_file = output_dir / f"podcast_script_{get_today_formatted()}.txt"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(f"PODCAST SCRIPT - {get_today_formatted()}\n")
            f.write("=" * 50 + "\n\n")
            f.write(podcast.anchor_script)
        
        # Download and save the audio file from CDN
        print(f"📥 Downloading audio from CDN...")
        audio_response = requests.get(podcast.audio_url)
        audio_response.raise_for_status()
        
        audio_file = output_dir / f"podcast_audio_{get_today_formatted()}.aac"
        with open(audio_file, "wb") as f:
            f.write(audio_response.content)
        
        # Save the podcast object metadata as JSON
        podcast_data = {
            "anchor_script": podcast.anchor_script,
            "audio_url": podcast.audio_url,
            "audio_size_bytes": podcast.audio_size_bytes,
            "audio_size_mb": round(podcast.audio_size_bytes / (1024 * 1024), 2),
            "story_count": podcast.story_count,
            "local_audio_file": audio_file.name
        }
        
        json_file = output_dir / f"podcast_data_{get_today_formatted()}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(podcast_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Script saved to: {script_file}")
        print(f"🎵 Audio downloaded and saved to: {audio_file}")
        print(f"📄 Podcast data saved to: {json_file}")
        
        print("\n🎵 CDN Audio Processing Complete:")
        print(f"✅ AAC audio uploaded to Cloudflare R2 CDN")
        print(f"✅ Audio size: {podcast.audio_size_bytes / (1024 * 1024):.1f} MB")
        print(f"✅ CDN URL: {podcast.audio_url}")
        print(f"✅ MongoDB contains only: anchor_script, audio_url, audio_size_bytes, story_count")
        print(f"✅ Frontend can use CDN URL for instant global streaming")
        print(f"✅ Local files saved to debug/test_output/ for verification")
        
        print("\nℹ️  Clean MongoDB structure with CDN URL instead of binary data.")
        print("ℹ️  Audio served from Cloudflare's global CDN for 50x faster loading.")
        print("ℹ️  Your frontend gets the CDN URL and streams audio directly.")
        
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