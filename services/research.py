from __future__ import annotations

from typing import List

from clients.perplexity import PerplexityClient
from config.prompts import ARTICLE_RESEARCH_TEMPLATE
from utils.logger import logger
from utils.models import Article, Event


def research_events(events: List[Event], *, perplexity_client: PerplexityClient) -> List[Article]:
    """Calls Perplexity once per event to generate full articles."""

    articles: list[Article] = []

    for event in events:
        prompt = ARTICLE_RESEARCH_TEMPLATE.format(event_summary=event.summary)
        response_text = perplexity_client.research(prompt)
        logger.debug("Perplexity response for '%s': %s", event.title, response_text)
        article = _parse_article_from_response(response_text)
        articles.append(article)

    logger.info("Generated %d articles.", len(articles))
    return articles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

import json
import re

_FENCE_REGEX = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)


def _parse_article_from_response(response_text: str) -> Article:
    """Parses the JSON (with optional fences) returned by Perplexity."""
    # Ideally no fences due to structured output, but guard just in case
    match = _FENCE_REGEX.search(response_text)
    json_str = match.group(1) if match else response_text

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:  # pragma: no cover
        logger.warning("Failed to parse article JSON: %s", exc)
        data = {
            "headline": "",
            "summary": "",
            "story": response_text,
            "sources": [],
        }

    return Article(
        headline=data.get("headline", ""),
        summary=data.get("summary", ""),
        story=data.get("story", ""),
        sources=data.get("sources", []),
    )