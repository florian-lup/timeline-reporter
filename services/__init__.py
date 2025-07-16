"""Services package for the timeline reporter project.

This package provides the core pipeline services:
- Discovery: Finding current events
- Deduplication: Removing similar events
- Decision: Prioritizing most impactful events
- Research: Creating full articles from events
- Storage: Saving articles to MongoDB
"""

from .article_insertion import insert_articles
from .article_research import research_articles
from .lead_deduplication import deduplicate_leads
from .lead_discovery import discover_leads
from .lead_curation import curate_leads

__all__ = [
    # Core pipeline services
    "discover_leads",
    "deduplicate_leads",
    "curate_leads",
    "research_articles",
    "insert_articles",
]
