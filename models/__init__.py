"""Models package for the timeline reporter project.

This package provides the core domain models:
- Lead: Represents news leads discovered in the pipeline
- Story: Represents fully-researched stories to be stored
"""

from .core import Lead, Story

__all__ = [
    "Lead",
    "Story",
]
