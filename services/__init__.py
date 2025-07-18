"""Services package for the timeline reporter project.

This package provides the core pipeline services:
- Discovery: Finding current leads
- Deduplication: Removing similar leads
- Decision: Prioritizing most impactful leads
- Research: Creating full stories from leads
- Storage: Saving stories to MongoDB
"""

from .lead_curation import LeadCurator, curate_leads
from .lead_deduplication import deduplicate_leads
from .lead_discovery import discover_leads
from .story_persistence import persist_stories
from .lead_research import research_lead

__all__ = [
    # Core pipeline services
    "discover_leads",
    "deduplicate_leads",
    "curate_leads",
    "research_lead",
    "persist_stories",
    # Advanced curation
    "LeadCurator",
]
