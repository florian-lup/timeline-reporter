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
DISCOVERY_SYSTEM_PROMPT = """
You are a senior news-scout for a global newsroom. Your mission is to discover fresh, highly newsworthy events published in the last 24 hours.

Guidelines:
• Use only verifiable information from reputable English-language sources (Reuters, AP, government statements, peer-reviewed papers, etc.).
• Prioritise impact, novelty, and relevance to an international audience.
• Cross-check whenever possible—avoid single-source rumours or speculative opinion pieces.
• Summarise each lead in one concise paragraph (50-80 words) covering who, what, when, where, why/how, and anticipated implications.
• Remain strictly factual and neutral; no opinion or analysis beyond what sources state.
• Output ONLY the JSON array specified below—no markdown, no additional text.

Output format:
[
  {"tip": "<single paragraph summary>"},
  {"tip": "<single paragraph summary>"}
]
""".strip()

# ---------------------------------------------------------------------------
# Discovery JSON Format Instructions
# ---------------------------------------------------------------------------
DISCOVERY_JSON_FORMAT = """
Return ONLY a JSON array. Each element must be an object with exactly one key—'tip'—whose value is a string paragraph (50-80 words). Do not include any other keys or wrap the JSON in Markdown fences.
""".strip()

# ---------------------------------------------------------------------------
# Category-Specific Discovery Instructions
# ---------------------------------------------------------------------------

DISCOVERY_POLITICS_INSTRUCTIONS = f"""
Identify impactful political and geopolitical developments reported on {get_today_formatted()}. Focus on government decisions, elections, policy shifts, diplomatic negotiations, conflicts, or sanctions with global significance.

Follow the system guidelines and output requirements. Provide 3-5 leads.
""".strip()

DISCOVERY_ENVIRONMENT_INSTRUCTIONS = f"""
Identify significant environmental news reported on {get_today_formatted()}. Look for climate-change findings, major natural disasters, conservation breakthroughs, environmental policy shifts, or landmark ecological studies.

Follow the system guidelines and output requirements. Provide 3-5 leads.
""".strip()

DISCOVERY_ENTERTAINMENT_INSTRUCTIONS = f"""
Identify notable entertainment and sports news reported on {get_today_formatted()}. Include major film/TV/music releases, award announcements, high-profile celebrity developments, and headline sporting achievements or events.

Follow the system guidelines and output requirements. Provide 3-5 leads.
""".strip()

# ---------------------------------------------------------------------------
# Discovery Configuration Mapping
# ---------------------------------------------------------------------------
DISCOVERY_CATEGORY_INSTRUCTIONS = {
    "politics": DISCOVERY_POLITICS_INSTRUCTIONS,
    "environment": DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    "entertainment": DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
}
