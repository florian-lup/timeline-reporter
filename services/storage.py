from __future__ import annotations

from typing import List

from clients.mongodb import MongoDBClient
from utils import logger, Article


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def store_articles(articles: List[Article], *, mongodb_client: MongoDBClient) -> None:
    """Stores articles in MongoDB."""

    for article in articles:
        article_dict = article.__dict__.copy()
        inserted_id = mongodb_client.insert_article(article_dict)
        logger.info("Stored article '%s' (id=%s)", article.headline, inserted_id)