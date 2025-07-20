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
# Discovery Timeout Configuration
# ---------------------------------------------------------------------------
DISCOVERY_TIMEOUT_SECONDS: float = 240  # Total timeout for discovery operations

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
Today is {get_today_formatted()}. You are an investigative news scout for a global newsroom tasked with identifying fresh, highly newsworthy leads that have emerged today.

Operational protocol:
• Remain strictly factual and neutral; do NOT speculate or extrapolate beyond what sources state, never fabricate data.
• Prioritize global coverage across different regions and countries, not just major markets.
• For every qualifying lead, provide only a concise title summarizing the key newsworthy development.
• Write in concise journalistic style (present tense, active voice).
• OUTPUT ONLY the JSON array described below—no markdown, no extra commentary, no extra text.

Expected output schema (do not include this block in your response):
[
  {{
    "title": "<concise summary of the newsworthy development>"
  }}
]
""".strip()

# ---------------------------------------------------------------------------
# Category-Specific Discovery Instructions
# ---------------------------------------------------------------------------

DISCOVERY_POLITICS_INSTRUCTIONS = f"""
Identify the most impactful political or geopolitical developments reported today.

""".strip()

DISCOVERY_ENVIRONMENT_INSTRUCTIONS = f"""
Identify 3-5 significant environmental developments reported today.

Prioritise stories involving:
• Landmark climate-change research, reports, or policy actions
• Natural disasters and validated impact assessments
• Breakthrough conservation efforts or ecological discoveries
• Major environmental legislation or court rulings

""".strip()

DISCOVERY_ENTERTAINMENT_INSTRUCTIONS = f"""
Identify 3-5 notable entertainment or sports developments reported today.

Include qualifying leads such as:
• Major film/TV/music releases, record-breaking box-office or streaming milestones
• Award announcements, festival premieres, or critical accolades
• High-profile, well-sourced celebrity developments
• Championship outcomes or record-setting sporting achievements

""".strip()

# ---------------------------------------------------------------------------
# Discovery Configuration Mapping
# ---------------------------------------------------------------------------
DISCOVERY_CATEGORY_INSTRUCTIONS = {
    "politics": DISCOVERY_POLITICS_INSTRUCTIONS,
    "environment": DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    "entertainment": DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
}
