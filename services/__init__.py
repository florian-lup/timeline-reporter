"""Services package for the timeline reporter project.

This package provides the core pipeline services:
- Discovery: Finding current leads
- Deduplication: Removing similar leads
- Research: Gathering context and sources for leads
- Decision: Prioritizing most impactful leads
- Writing: Creating full stories from researched leads
- Storage: Saving stories to MongoDB
"""

from .lead_curation import LeadCurator, curate_leads
from .lead_deduplication import deduplicate_leads
from .lead_discovery import discover_leads
from .lead_research import research_lead
from .story_persistence import persist_stories
from .story_writing import write_stories

__all__ = [
    # Core pipeline services
    "discover_leads",
    "deduplicate_leads",
    "research_lead",
    "curate_leads",
    "write_stories",
    "persist_stories",
    # Advanced curation
    "LeadCurator",
]
