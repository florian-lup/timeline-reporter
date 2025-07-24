"""Centralized configuration for lead discovery system.

This module contains all settings, prompts, and configuration data
related to lead discovery across different news categories.
"""

from utils import get_today_formatted, get_today_api_format

# ---------------------------------------------------------------------------
# Discovery Model Configuration
# ---------------------------------------------------------------------------
LEAD_DISCOVERY_MODEL: str = "sonar-reasoning-pro"
SEARCH_CONTEXT_SIZE: str = "high"
SEARCH_AFTER_DATE_FILTER: str = get_today_api_format()  # Only content from today

# ---------------------------------------------------------------------------
# Discovery Timeout Configuration
# ---------------------------------------------------------------------------
DISCOVERY_TIMEOUT_SECONDS: float = 300  # Total timeout for discovery operations

# ---------------------------------------------------------------------------
# Discovery JSON Schema Configuration
# ---------------------------------------------------------------------------

# JSON schema for Discovery structured output (array of leads)
LEAD_DISCOVERY_JSON_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "lead_summary": {"type": "string"},
        },
        "required": ["lead_summary"],
    },
}

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
DISCOVERY_SYSTEM_PROMPT = f"""
You are an investigative news scout for a global newsroom tasked with identifying fresh, highly newsworthy leads that have emerged today {get_today_formatted()}.

Operational protocol:
• Remain strictly factual and neutral; do NOT speculate or extrapolate beyond what sources state, never fabricate data.
• Prioritize global coverage across different regions and countries, not just major markets.
• For every qualifying lead, provide a 50 - 100 words summarizing who, what, when, where, why, and how.
• Write in concise journalistic style (present tense, active voice).
• OUTPUT ONLY the JSON array described below—no markdown, no extra commentary, no extra text.

Expected output schema (do not include this block in your response):
[
  {{
    "lead_summary": "summary of the qualifying lead"
  }}
]
""".strip()

# ---------------------------------------------------------------------------
# Category-Specific Discovery Instructions
# ---------------------------------------------------------------------------

DISCOVERY_POLITICS_INSTRUCTIONS = f"""
Identify as many significant political or geopolitical developments as possible reported today {get_today_formatted()}. Maximize breadth and coverage—include global, national, regional, and local developments, as well as both emerging and ongoing stories.

Follow these guidelines:
• Include all qualifying leads, not just the most impactful.
• Cover a wide range of topics: elections, government actions, policy changes, international relations, conflicts, treaties, protests, leadership changes, major legislation, and court rulings.
• Prioritize diversity of regions and countries—do not focus solely on major powers.
• For each lead, ensure it is well-sourced and factually reported.
• Avoid duplicates and overlapping stories.

""".strip()

DISCOVERY_ENVIRONMENT_INSTRUCTIONS = f"""
Identify as many significant environmental developments as possible reported today {get_today_formatted()}. Maximize breadth and coverage—include global, national, regional, and local developments, as well as both emerging and ongoing stories.

Follow these guidelines:
• Include all qualifying leads, not just the most impactful.
• Cover a wide range of topics: climate change developments, environmental policy announcements, natural disasters, conservation efforts, pollution incidents, scientific discoveries, corporate environmental actions, renewable energy projects, and environmental activism.
• Prioritize diversity of regions and countries—do not focus solely on major powers.
• For each lead, ensure it is well-sourced and factually reported.
• Avoid duplicates and overlapping stories.

""".strip()

DISCOVERY_ENTERTAINMENT_INSTRUCTIONS = f"""
Identify as many significant entertainment industry developments as possible reported today {get_today_formatted()}. Maximize breadth and coverage—include global, national, regional, and local developments, as well as both emerging and ongoing stories.

Follow these guidelines:
• Include all qualifying leads, not just the most impactful.
• Cover a wide range of topics: celebrity news, film and television announcements, music industry developments, awards and premieres, box office results, streaming platform updates, entertainment business deals, cultural events, and industry controversies.
• Prioritize diversity of regions and countries—do not focus solely on major markets like Hollywood or major streaming platforms.
• For each lead, ensure it is well-sourced and factually reported.
• Avoid duplicates and overlapping stories.

""".strip()

# ---------------------------------------------------------------------------
# Discovery Configuration Mapping
# ---------------------------------------------------------------------------
DISCOVERY_CATEGORY_INSTRUCTIONS = {
    "politics": DISCOVERY_POLITICS_INSTRUCTIONS,
    "environment": DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    "entertainment": DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
}
