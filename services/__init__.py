"""Services package for the timeline reporter project.

This package provides the core pipeline services:
- Discovery: Finding current events
- Deduplication: Removing similar events
- Decision: Prioritizing most impactful events
- Research: Creating full articles from events  
- TTS: Converting articles to audio broadcasts
- Storage: Saving articles to MongoDB
"""

from .event_deduplication import deduplicate_events
from .event_selection import select_events
from .event_discovery import discover_events
from .article_research import research_articles
from .article_insertion import insert_articles
from .audio_generation import generate_audio

__all__ = [
    # Core pipeline services
    "discover_events",
    "deduplicate_events",
    "select_events", 
    "research_articles",
    "insert_articles",
    "generate_audio",
] 