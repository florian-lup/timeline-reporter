from __future__ import annotations

from dataclasses import dataclass, field

from utils.date import get_today_formatted


@dataclass
class Event:
    """Represents a news event discovered in the discovery step."""

    title: str
    summary: str
    date: str = field(default_factory=get_today_formatted)


@dataclass
class Article:
    """Represents a fully-fledged researched article to be stored in MongoDB."""

    headline: str
    summary: str
    story: str
    sources: list[str]
    broadcast: bytes
    reporter: str
    date: str = field(default_factory=get_today_formatted)
