"""Centralized configuration for lead discovery system.

This module contains all settings, prompts, and configuration data
related to lead discovery across different news categories.
"""

from utils import get_today_formatted

# ---------------------------------------------------------------------------
# Discovery Model Configuration
# ---------------------------------------------------------------------------
LEAD_DISCOVERY_MODEL: str = "sonar-reasoning-pro"
SEARCH_CONTEXT_SIZE: str = "high"

# ---------------------------------------------------------------------------
# Discovery Categories Configuration
# ---------------------------------------------------------------------------
DISCOVERY_CATEGORIES = [
    "politics",
    "environment",
    "entertainment",
]

# ---------------------------------------------------------------------------
# Discovery System Prompt
# ---------------------------------------------------------------------------
DISCOVERY_SYSTEM_PROMPT = (
    "You are an expert research assistant specializing in identifying "
    "significant current events. Focus on finding factual, newsworthy "
    "developments from reputable sources. Provide comprehensive summaries "
    "that capture the key details and implications of each lead."
    "\n\nStructure your response as a JSON array where each "
    "lead has a 'tip' field containing a comprehensive paragraph "
    "summarizing the lead's significance and key details. Format: "
    '[{"tip": "Comprehensive paragraph describing the lead, its '
    'significance, and key details..."}]'
)

# ---------------------------------------------------------------------------
# Category-Specific Discovery Instructions
# ---------------------------------------------------------------------------

DISCOVERY_POLITICS_INSTRUCTIONS = (
    f"Identify significant news about politics, geopolitics, and governments "
    f"from today {get_today_formatted()}. Focus on major political developments, "
    "international relations, policy changes, elections, diplomatic events, "
    "and governmental decisions that would be of interest to a global audience. "
    "Return your findings as a JSON array of leads, where each "
    "lead has a 'tip' field containing a comprehensive paragraph "
    "explaining the lead with all key details and implications. Example format: "
    '[{"tip": "Comprehensive paragraph describing the political lead, its '
    'significance, and key details..."}]'
)

DISCOVERY_ENVIRONMENT_INSTRUCTIONS = (
    f"Identify significant news about environment, climate, and natural disasters "
    f"from today {get_today_formatted()}. Focus on climate change developments, "
    "environmental policies, natural disasters, conservation efforts, "
    "extreme weather events, and ecological breakthroughs that would be of "
    "interest to a global audience. Return your findings as a JSON array of leads, "
    "where each lead has a 'tip' field containing a comprehensive paragraph "
    "explaining the lead with all key details and implications. Example format: "
    '[{"tip": "Comprehensive paragraph describing the environmental lead, its '
    'significance, and key details..."}]'
)

DISCOVERY_ENTERTAINMENT_INSTRUCTIONS = (
    f"Identify significant news about celebrities, entertainment, and sports "
    f"from today {get_today_formatted()}. Focus on major celebrity news, "
    "entertainment industry developments, film and music releases, major sporting "
    "achievements, championship events, and cultural phenomena that would be of "
    "interest to a global audience. Return your findings as a JSON array of leads, "
    "where each lead has a 'tip' field containing a comprehensive paragraph "
    "explaining the lead with all key details and implications. Example format: "
    '[{"tip": "Comprehensive paragraph describing the entertainment/sports lead, its '
    'significance, and key details..."}]'
)

# ---------------------------------------------------------------------------
# Discovery Configuration Mapping
# ---------------------------------------------------------------------------
DISCOVERY_CATEGORY_INSTRUCTIONS = {
    "politics": DISCOVERY_POLITICS_INSTRUCTIONS,
    "environment": DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    "entertainment": DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
}
