"""Models package for the timeline reporter project.

This package provides the core domain models:
- Lead: Represents news leads discovered in the pipeline
- Article: Represents fully-researched articles to be stored
"""

from .core import Article, Lead

__all__ = [
    "Lead",
    "Article",
] 