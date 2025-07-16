"""Services package for the timeline reporter project.

This package provides the core pipeline services:
- Discovery: Finding current events
- Deduplication: Removing similar events
- Decision: Prioritizing most impactful events
- Research: Creating full stories from events
- Storage: Saving stories to MongoDB
"""

from .story_persistence import persist_stories
from .story_research import research_story
from .lead_deduplication import deduplicate_leads
from .lead_discovery import discover_leads
from .lead_curation import curate_leads

__all__ = [
    # Core pipeline services
    "discover_leads",
    "deduplicate_leads",
    "curate_leads",
    "research_story",
    "persist_stories",
]
