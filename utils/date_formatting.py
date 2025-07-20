"""Date utilities for the timeline reporter project."""

from datetime import date


def get_today_formatted() -> str:
    """Returns today's date in a human-readable format for prompts."""
    return date.today().strftime("%d %B %Y")
