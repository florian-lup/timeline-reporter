from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Event:
    """Represents a news event discovered in the discovery step."""

    title: str
    summary: str


@dataclass
class Article:
    """Represents a fully-fledged researched article to be stored in MongoDB."""

    headline: str
    summary: str
    story: str
    sources: List[str]
    broadcast: bytes     # MP3 audio data
    reporter: str        # Human name of the reporter voice 