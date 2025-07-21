from __future__ import annotations

from dataclasses import dataclass, field

from utils.date_formatting import get_today_formatted


@dataclass
class Lead:
    """Represents a news lead discovered in the discovery step."""

    title: str
    report: str = ""
    sources: list[str] = field(default_factory=list)
    date: str = field(default_factory=get_today_formatted)


@dataclass
class Story:
    """Represents a fully-fledged researched story to be stored in MongoDB."""

    headline: str
    summary: str
    body: str
    tag: str
    sources: list[str]
    date: str = field(default_factory=get_today_formatted)


@dataclass
class Podcast:
    """Represents an audio podcast generated from story summaries."""

    anchor_script: str
    audio_file: bytes
    story_count: int
