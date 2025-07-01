"""Services package for the timeline reporter project.

This package provides the core pipeline services:
- Discovery: Finding current events
- Deduplication: Removing similar events
- Decision: Prioritizing most impactful events
- Research: Creating full articles from events  
- TTS: Converting articles to audio broadcasts
- Storage: Saving articles to MongoDB
"""

from .deduplication import deduplicate_events
from .decision import decide_events
from .discovery import discover_events
from .research import research_events
from .storage import store_articles
from .tts import generate_broadcast_analysis

__all__ = [
    # Core pipeline services
    "discover_events",
    "deduplicate_events",
    "decide_events", 
    "research_events",
    "generate_broadcast_analysis",
    "store_articles",
] 