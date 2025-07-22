"""Centralized configuration for lead research system.

This module contains all settings, prompts, and configuration data
related to lead research and source gathering.
"""

# ---------------------------------------------------------------------------
# Research Model Configuration
# ---------------------------------------------------------------------------
LEAD_RESEARCH_MODEL: str = "sonar-reasoning-pro"
SEARCH_CONTEXT_SIZE: str = "high"

# ---------------------------------------------------------------------------
# Research Timeout Configuration  
# ---------------------------------------------------------------------------
RESEARCH_TIMEOUT_SECONDS: float = 240  # Total timeout for research operations

# ---------------------------------------------------------------------------
# Research System Prompt
# ---------------------------------------------------------------------------
RESEARCH_SYSTEM_PROMPT = """
You are a senior investigative research analyst at a global news desk.
Your job is to collect verifiable facts and authoritative sources about developing news leads.

Guidelines:
• Prioritize primary documents (official statements, court filings, scientific papers) and well-established outlets (Reuters, Associated Press, BBC).
• Avoid speculative commentary and opinion pieces unless they are central to the lead—and clearly label them.
• Remain neutral and avoid political or ideological bias.
• Provide an in-depth report (≈ 600–1000 words) detailing relevant background, key actors, chronology, significance, and controversies.
• Write in a clear, professional journalistic style.
""".strip()

# ---------------------------------------------------------------------------
# Research Instructions Template
# ---------------------------------------------------------------------------
RESEARCH_INSTRUCTIONS = """
Research and provide comprehensive background information about the following news lead.

Lead Title: {lead_title}

Provide detailed context, background information, key stakeholders, timeline of events, and significance. Focus on verifiable facts from authoritative sources.
""".strip()


