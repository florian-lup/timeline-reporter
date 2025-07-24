from __future__ import annotations

from dataclasses import dataclass, field

from utils.date_formatting import get_today_formatted


@dataclass
class Lead:
    """Represents a news lead discovered in the discovery step."""

    discovered_lead: str
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
    anchor_name: str
    audio_url: str
    audio_size_bytes: int


@dataclass
class LeadEvaluation:
    """Comprehensive evaluation of a lead."""

    lead: Lead
    criteria_scores: dict[str, float]  # Individual criteria scores
    weighted_score: float  # Overall weighted score
    pairwise_wins: int = 0  # Number of pairwise comparisons won
    final_rank: float = 0.0  # Final ranking after all evaluations
