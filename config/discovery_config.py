"""Centralized configuration for lead discovery system.

This module contains all settings, prompts, and configuration data
related to lead discovery across different news categories.
"""

from utils import get_today_formatted

# ---------------------------------------------------------------------------
# Discovery Model Configuration
# ---------------------------------------------------------------------------
LEAD_DISCOVERY_MODEL: str = "sonar-deep-research"
SEARCH_CONTEXT_SIZE: str = "low"
REASONING_EFFORT: str = "low"

# ---------------------------------------------------------------------------
# Discovery Timeout Configuration
# ---------------------------------------------------------------------------
DISCOVERY_TIMEOUT_SECONDS: float = 600  # Total timeout for discovery operations

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
You are a senior news-scout for a global newsroom charged with surfacing fresh, highly newsworthy events published in the last 24 hours.

Guidelines:
• Use only verifiable information from reputable English-language sources that are publicly accessible
  (Reuters, AP, government releases, peer-reviewed papers, etc.).
• Be specific and contextual: focus your search on well-defined keywords that journalists and experts would use.
• Avoid few-shot examples or unnecessary formatting instructions that could confuse search relevance.
• If information is insufficient or no qualifying leads are found, return an empty JSON array ( [] )—do NOT fabricate content.
• Cross-check whenever possible—avoid single-source rumours or speculative opinion pieces.
• Summarise each lead in one concise paragraph (50-80 words) covering who, what, when, where, why/how, and implications.
• Include credible source URLs that confirm the information in your summary.
• Remain strictly factual and neutral; no opinion or analysis beyond what the sourced material states.
• OUTPUT ONLY the JSON array described below—no markdown, headers, or extra commentary.

Expected output format (do not include this block in your response):
[
  {"tip": "<single paragraph summary>", "sources": ["<source_url_1>", "<source_url_2>"]},
  {"tip": "<single paragraph summary>", "sources": ["<source_url_1>", "<source_url_2>"]}
]
""".strip()

# ---------------------------------------------------------------------------
# Discovery JSON Format Instructions
# ---------------------------------------------------------------------------
DISCOVERY_JSON_FORMAT = """
Return ONLY a JSON array. Each element must be an object with exactly two keys:
- 'tip': a single-paragraph string (50-80 words)
- 'sources': an array of credible source URLs that confirm the information

Do NOT include any other keys, wrap the output in Markdown fences, or add explanations before/after the JSON. 
If no leads meet the criteria, return an empty array: []
""".strip()

# ---------------------------------------------------------------------------
# Discovery Recency Filter Configuration
# ---------------------------------------------------------------------------
SEARCH_RECENCY_FILTER: str = "day"  # Limit web search to content from the last 24 hours

# ---------------------------------------------------------------------------
# Category-Specific Discovery Instructions
# ---------------------------------------------------------------------------

DISCOVERY_POLITICS_INSTRUCTIONS = f"""
Today is {get_today_formatted()}. Identify 3-5 impactful political or geopolitical developments reported within the past 24 hours. Focus on:
• Government decisions, policy shifts, or legislative milestones
• Key elections or leadership changes
• Diplomatic negotiations, sanctions, or conflict escalations with global repercussions

If reliable sources cannot be found for a potential lead, omit it rather than speculate. Follow the system-level guidelines and output requirements.
""".strip()

DISCOVERY_ENVIRONMENT_INSTRUCTIONS = f"""
Today is {get_today_formatted()}. Identify 3-5 significant environmental stories reported within the past 24 hours. Look for:
• Major climate-change findings or reports
• Natural disasters and their verified impacts
• Landmark conservation efforts or policy shifts
• Breakthrough ecological research

Omit any lead that lacks corroboration from reputable sources. Follow the system-level guidelines and output requirements.
""".strip()

DISCOVERY_ENTERTAINMENT_INSTRUCTIONS = f"""
Today is {get_today_formatted()}. Identify 3-5 notable entertainment or sports stories reported within the past 24 hours. Include:
• Major film/TV/music releases or box-office milestones
• Award announcements or festival highlights
• High-profile celebrity developments confirmed by credible outlets
• Championship outcomes or record-breaking sporting achievements

Exclude rumours or unverified gossip. Follow the system-level guidelines and output requirements.
""".strip()

# ---------------------------------------------------------------------------
# Discovery Configuration Mapping
# ---------------------------------------------------------------------------
DISCOVERY_CATEGORY_INSTRUCTIONS = {
    "politics": DISCOVERY_POLITICS_INSTRUCTIONS,
    "environment": DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    "entertainment": DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
}
