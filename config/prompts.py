"""Centralized prompts for the timeline-reporter AI pipeline.

This module contains all the prompts used across different services and clients
to maintain consistency and make updates easier.
"""

# ---------------------------------------------------------------------------
# Discovery Prompts
# ---------------------------------------------------------------------------

DISCOVERY_INSTRUCTIONS = (
    "You are tasked with identifying significant news about {topics} "
    "from today {date}. Provide your answer strictly as JSON with the "
    "following format:\n\n[\n  {{\n    \"title\": <short headline>,\n    \"summary\": <~300 word summary>\n  }}\n]\n\nDo not include any additional keys, commentary, or markdown."
)

# ---------------------------------------------------------------------------
# OpenAI Deep Research Prompts
# ---------------------------------------------------------------------------

OPENAI_DEEP_RESEARCH_SYSTEM_PROMPT = (
    "You are an expert research assistant. Compile structured, "
    "factual results only from reputable sources. Provide your answer strictly as JSON with the following format:\n\n"
    "[\n  {\n    \"title\": <short headline>,\n    \"summary\": <~300 word summary>\n  }\n]\n\n"
    "Do not include any additional keys, commentary, or markdown."
)

# ---------------------------------------------------------------------------
# Research & Article Generation Prompts
# ---------------------------------------------------------------------------

ARTICLE_RESEARCH_TEMPLATE = (
    "Using the information provided below, craft a well-structured news article.\n\n"
    "Event:\n{event_summary}\n\n"
    "The article must be returned strictly as JSON with the following keys:\n"
    "headline (max 20 words), summary (80-120 words), story (400-600 words), sources (array of URLs)."
)

# ---------------------------------------------------------------------------
# Perplexity Client Prompts
# ---------------------------------------------------------------------------

PERPLEXITY_JOURNALIST_SYSTEM_PROMPT = (
    "You are an investigative journalist. Respond ONLY with a JSON object "
    "following the provided schema. Do NOT include markdown fences or commentary."
)

# ---------------------------------------------------------------------------
# Prompt Categories for Easy Access
# ---------------------------------------------------------------------------

DISCOVERY_PROMPTS = {
    "instructions": DISCOVERY_INSTRUCTIONS,
}

RESEARCH_PROMPTS = {
    "openai_system": OPENAI_DEEP_RESEARCH_SYSTEM_PROMPT,
    "article_template": ARTICLE_RESEARCH_TEMPLATE,
    "perplexity_system": PERPLEXITY_JOURNALIST_SYSTEM_PROMPT,
}

# All prompts for easy iteration/management
ALL_PROMPTS = {
    "discovery": DISCOVERY_PROMPTS,
    "research": RESEARCH_PROMPTS,
}
