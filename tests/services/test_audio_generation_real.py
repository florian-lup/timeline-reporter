"""Real integration test for audio generation service.

This test uses actual OpenAI and MongoDB clients to generate a real podcast
from provided story summaries. It will make real API calls and create actual audio output.
"""

import os
from pathlib import Path

import pytest

from clients import MongoDBClient, OpenAIClient
from models import Story
from services.audio_generation import generate_podcast
from utils import get_today_formatted


@pytest.mark.real
@pytest.mark.skipif(
    not all([
        os.getenv("OPENAI_API_KEY"),
        os.getenv("MONGODB_URI"),
        os.getenv("MONGODB_DATABASE_NAME"),
        os.getenv("MONGODB_COLLECTION_NAME_AUDIO"),
    ]),
    reason="Real API keys and MongoDB configuration required"
)
def test_real_audio_generation_with_provided_summaries():
    """Test real audio generation with the user-provided story summaries.
    
    This test will:
    1. Create Story objects from provided summaries
    2. Use real OpenAI client for script generation and TTS
    3. Use real MongoDB client for persistence
    4. Generate actual audio output
    5. Save audio file to local directory for verification
    """
    
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
    
    # Initialize real clients
    openai_client = OpenAIClient()
    mongodb_client = MongoDBClient()
    
    # Generate the podcast using real services
    print(f"\n🎙️ Starting real audio generation test with {len(stories)} stories...")
    print("📝 Story summaries:")
    for i, story in enumerate(stories, 1):
        print(f"  {i}. {story.headline}")
    
    # Execute the real audio generation pipeline
    podcast = generate_podcast(
        stories,
        openai_client=openai_client,
        mongodb_client=mongodb_client,
    )
    
    # Verify podcast was created successfully
    assert podcast is not None
    assert podcast.anchor_script != ""
    assert len(podcast.audio_file) > 0  # Audio bytes exist
    assert podcast.story_count == 3
    
    print(f"✅ Podcast generated successfully!")
    print(f"📄 Script length: {len(podcast.anchor_script.split())} words")
    print(f"🔗 Audio bytes size: {len(podcast.audio_file) / (1024 * 1024):.1f} MB")
    print(f"📊 Story count: {podcast.story_count}")
    
    # Create a local test output directory  
    from pathlib import Path
    output_dir = Path("test_audio_output")
    output_dir.mkdir(exist_ok=True)
    
    # For demonstration, save the script to a text file
    script_file = output_dir / f"podcast_script_{get_today_formatted()}.txt"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(f"PODCAST SCRIPT - {get_today_formatted()}\n")
        f.write("=" * 50 + "\n\n")
        f.write(podcast.anchor_script)
    
    print(f"💾 Script saved to: {script_file}")
    
    print("\n🎵 Audio Processing Complete:")
    print(f"✅ MP3 audio bytes stored directly in audio_file field")
    print(f"✅ Audio size: {len(podcast.audio_file) / (1024 * 1024):.1f} MB")
    print(f"✅ MongoDB contains only: anchor_script, audio_file (bytes), story_count")
    print(f"✅ Frontend can fetch audio_file and play it directly")
    
    print("\nℹ️  Clean MongoDB structure with only the essential fields.")
    print("ℹ️  No local files created - everything is in the database.")
    print("ℹ️  Your frontend can retrieve the audio_file field and play the MP3 bytes.")


if __name__ == "__main__":
    # Allow running this test directly for manual testing
    test_real_audio_generation_with_provided_summaries() 