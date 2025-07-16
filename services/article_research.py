from __future__ import annotations

import json
import re

from clients import PerplexityClient
from config import RESEARCH_INSTRUCTIONS
from models import Lead, Story
from utils import logger
from utils.date import get_today_formatted


def research_articles(
    leads: list[Lead], *, perplexity_client: PerplexityClient
) -> list[Story]:
    """Calls Perplexity once per lead to generate full articles."""
    articles: list[Story] = []

    for lead in leads:
        prompt = RESEARCH_INSTRUCTIONS.format(
            event_summary=lead.context, event_date=lead.date
        )
        response_text = perplexity_client.research(prompt)
        article = _parse_article_from_response(response_text)
        articles.append(article)

    logger.info("Generated %d articles", len(articles))
    return articles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_article_from_response(response_text: str) -> Story:
    """Parse JSON from Perplexity and return a Story object."""
    # Some models wrap JSON in markdown triple-backticks; strip them if needed.
    fence_regex = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)
    match = fence_regex.search(response_text)
    json_blob = match.group(1) if match else response_text

    try:
        data = json.loads(json_blob)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("JSON parse failed: %s", exc)
        # Return a minimal Story with empty content
        return Story(
            headline="",
            summary="",
            body="",
            sources=[],
        )

    # Create Story from the JSON data, with fallbacks for missing fields
    return Story(
        headline=data.get("headline", ""),
        summary=data.get("summary", ""),
        body=data.get("body", ""),
        sources=data.get("sources", []),
        date=data.get("date", get_today_formatted()),  # Use date from JSON or default
    )
