"""Utilities package for the timeline reporter project.

This package provides common utilities including:
- Date formatting functions
- Logging configuration
- URL normalization and deduplication
"""

from .date_formatting import get_today_api_format, get_today_formatted
from .logger import logger
from .url_deduplication import combine_and_deduplicate_sources, deduplicate_sources, normalize_url

__all__ = [
    # Date utilities
    "get_today_formatted",
    "get_today_api_format",
    # Logging
    "logger",
    # URL utilities
    "normalize_url",
    "deduplicate_sources",
    "combine_and_deduplicate_sources",
]
