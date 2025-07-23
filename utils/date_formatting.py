"""Date utilities for the timeline reporter project."""

from datetime import date


def get_today_formatted() -> str:
    """Returns today's date in a human-readable format for prompts."""
    return date.today().strftime("%d %B %Y")


def get_today_api_format() -> str:
    """Returns today's date in MM/DD/YYYY format for API date filters."""
    today = date.today()
    # Format without leading zeros for cross-platform compatibility
    return f"{today.month}/{today.day}/{today.year}"
