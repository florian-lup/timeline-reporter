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
Today is {get_today_formatted()}. You are an investigative news scout for a global newsroom tasked with identifying fresh, highly newsworthy leads that have emerged within the last 24 hours.

Operational protocol:
• Perform iterative web research: generate precise keyword sets, run targeted searches, open and skim promising results, verify publication date (≤ 24 h), and cross-check facts across multiple independent, authoritative English-language sources.
• Remain strictly factual and neutral; do NOT speculate or extrapolate beyond what sources state.
• If information is insufficient or no qualifying leads are found, output an empty JSON array ( [] )—never fabricate data.
• For every qualifying lead, provide:
  – title: 50-80 words summarising who, what, when, where, why/how, and significance.
  – report: a thorough analysis (at least 700 words) offering background, context, expert analysis, implications, and related developments.
  – sources: an array of all distinct, credible URLs you can find that corroborate the lead.
• Write in concise journalistic style (present tense, active voice).
• OUTPUT ONLY the JSON array described below—no markdown, no extra commentary.

Expected output schema (do not include this block in your response):
[
  {{
    "title": "<single paragraph summary>",
    "report": "<comprehensive detailed analysis>",
    "sources": ["<source_url_1>", "<source_url_2>"]
  }}
]
""".strip()

# ---------------------------------------------------------------------------
# Category-Specific Discovery Instructions
# ---------------------------------------------------------------------------

DISCOVERY_POLITICS_INSTRUCTIONS = f"""
Today is {get_today_formatted()}. Identify 3-5 impactful political or geopolitical developments reported within the past 24 hours.

Focus on developments such as:
• Government decisions, policy shifts, or legislative milestones
• Key elections or leadership changes
• Diplomatic negotiations, sanctions, or conflict escalations with global repercussions

For each qualifying lead:
1. title – 50-80 words summarising the who/what/when/where/why-how and significance.
2. report – a thorough analysis (≥ 700 words) covering:
   • Relevant background and timeline
   • Key stakeholders and their positions
   • Short- and long-term implications
   • Related or precedent developments
   • Attributed expert analysis or official statements
3. sources – as many credible URLs as you can find to corroborate the information

If reliable sources are lacking, omit the lead rather than speculate. Follow the system-level protocol and JSON output requirements exactly.
""".strip()

DISCOVERY_ENVIRONMENT_INSTRUCTIONS = f"""
Today is {get_today_formatted()}. Identify 3-5 significant environmental developments reported within the past 24 hours.

Prioritise stories involving:
• Landmark climate-change research, reports, or policy actions
• Natural disasters and validated impact assessments
• Breakthrough conservation efforts or ecological discoveries
• Major environmental legislation or court rulings

For each qualifying lead:
1. title – 50-80 words summarising the core facts and impact.
2. report – a thorough analysis (≥ 700 words) including:
   • Scientific background and methodology (for research leads)
   • Environmental impact scope and affected regions
   • Government, NGO, or industry responses
   • Connection to broader environmental trends
   • Expert commentary or scientific consensus with attribution
3. sources – as many credible URLs as you can find to corroborate the information

Exclude any unverified or speculative content. Adhere to the system-level protocol and JSON output requirements exactly.
""".strip()

DISCOVERY_ENTERTAINMENT_INSTRUCTIONS = f"""
Today is {get_today_formatted()}. Identify 3-5 notable entertainment or sports developments reported within the past 24 hours.

Include qualifying leads such as:
• Major film/TV/music releases, record-breaking box-office or streaming milestones
• Award announcements, festival premieres, or critical accolades
• High-profile, well-sourced celebrity developments
• Championship outcomes or record-setting sporting achievements

For each qualifying lead:
1. title – 50-80 words summarising the key details and relevance.
2. report – a thorough analysis (≥ 700 words) covering:
   • Background on personalities, productions, or events
   • Industry or competitive context and significance
   • Financial, cultural, or athletic impact
   • Fan, critic, or market reactions (with attribution)
   • Historical comparisons or precedents
3. sources – as many credible URLs as you can find from recognised outlets to corroborate the information

Omit rumours or unverified gossip. Follow the system-level protocol and JSON output requirements exactly.
""".strip()

# ---------------------------------------------------------------------------
# Discovery Configuration Mapping
# ---------------------------------------------------------------------------
DISCOVERY_CATEGORY_INSTRUCTIONS = {
    "politics": DISCOVERY_POLITICS_INSTRUCTIONS,
    "environment": DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    "entertainment": DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
}
