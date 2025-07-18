from __future__ import annotations

from dataclasses import dataclass, field

from utils.date import get_today_formatted


@dataclass
class Lead:
    """Represents a news lead discovered in the discovery step."""

    tip: str
    context: str =
    sources: list[str] = field(default_factory=list)
    date: str = field(default_factory=get_today_formatted)


@dataclass
class Story:
    """Represents a fully-fledged researched story to be stored in MongoDB."""

    headline: str
    summary: str
    body: str
    sources: list[str]
    date: str = field(default_factory=get_today_formatted)
