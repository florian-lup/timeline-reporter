"""URL utilities for the timeline reporter project.

This module provides functions for URL normalization and deduplication.
"""

from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent comparison.

    Handles common variations like:
    - Protocol normalization (http -> https when appropriate)
    - Removes trailing slashes
    - Removes common tracking parameters
    - Lowercases domain
    - Removes www prefix for consistency

    Args:
        url: The URL to normalize

    Returns:
        Normalized URL string
    """
    if not url or not isinstance(url, str):
        return url

    try:
        parsed = urlparse(url.strip())

        # Skip normalization for non-http(s) URLs
        if parsed.scheme not in ("http", "https"):
            return url

        # Normalize scheme to https if it's a known secure domain
        scheme = "https" if parsed.scheme in ("http", "https") else parsed.scheme

        # Normalize domain: lowercase and remove www prefix
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        # Remove trailing slash from path
        path = parsed.path.rstrip("/")

        # Remove common tracking parameters
        query_params = []
        if parsed.query:
            # Keep query if it doesn't look like tracking
            # Common tracking params: utm_*, fbclid, gclid, etc.
            tracking_prefixes = ("utm_", "fbclid", "gclid", "_ga", "mc_", "ref")
            params = parsed.query.split("&")
            for param in params:
                if "=" in param:
                    key = param.split("=")[0].lower()
                    if not any(key.startswith(prefix) for prefix in tracking_prefixes):
                        query_params.append(param)
                else:
                    query_params.append(param)

        query = "&".join(query_params) if query_params else ""

        # Reconstruct URL
        return urlunparse((scheme, netloc, path, parsed.params, query, parsed.fragment))

    except Exception:
        # If parsing fails, return original URL
        return url


def deduplicate_sources(sources: list[str]) -> list[str]:
    """Remove duplicate URLs from a list of sources.

    Uses URL normalization to catch variations of the same URL.

    Args:
        sources: List of URL strings

    Returns:
        List of unique URLs with duplicates removed
    """
    if not sources:
        return []

    seen_normalized = set()
    unique_sources = []

    for source in sources:
        if not source:  # Skip empty/None sources
            continue

        normalized = normalize_url(source)
        if normalized not in seen_normalized:
            seen_normalized.add(normalized)
            unique_sources.append(source)  # Keep original URL format

    return unique_sources


def combine_and_deduplicate_sources(existing_sources: list[str], new_sources: list[str]) -> list[str]:
    """Combine two lists of sources and remove duplicates.

    Args:
        existing_sources: Sources from discovery
        new_sources: Sources from research

    Returns:
        Combined list with duplicates removed
    """
    combined = (existing_sources or []) + (new_sources or [])
    return deduplicate_sources(combined)
