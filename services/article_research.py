from __future__ import annotations

import json
import re

from clients import PerplexityClient
from config import RESEARCH_INSTRUCTIONS
from models import Lead, Story
from utils import logger


def research_articles(
    events: list[Lead], *, perplexity_client: PerplexityClient
) -> list[Story]:
    """Calls Perplexity once per event to generate full articles."""
    articles: list[Story] = []

    for event in events:
        prompt = RESEARCH_INSTRUCTIONS.format(
            event_summary=event.summary, event_date=event.date
        )
        response_text = perplexity_client.research(prompt)
        article = _parse_article_from_response(response_text)
        articles.append(article)

    logger.info("Generated %d articles", len(articles))
    return articles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FENCE_REGEX = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)


def _parse_article_from_response(response_text: str) -> Story:
    """Parses the JSON (with optional fences) returned by Perplexity."""
    # Ideally no fences due to structured output, but guard just in case
    match = _FENCE_REGEX.search(response_text)
    json_str = match.group(1) if match else response_text

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("Article JSON parse failed: %s", exc)
        data = {
            "headline": "",
            "summary": "",
            "body": response_text,
            "sources": [],
        }

    return Story(
        headline=data.get("headline", "") or "",
        summary=data.get("summary", "") or "",
        body=data.get("body", "") or "",
        sources=data.get("sources", []) or [],
    )
