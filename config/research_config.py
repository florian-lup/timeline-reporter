"""Centralized configuration for lead research system.

This module contains all settings, prompts, and configuration data
related to lead research and source gathering.
"""

# ---------------------------------------------------------------------------
# Research Model Configuration
# ---------------------------------------------------------------------------
LEAD_RESEARCH_MODEL: str = "sonar-pro"

# ---------------------------------------------------------------------------
# Research System Prompt
# ---------------------------------------------------------------------------
RESEARCH_SYSTEM_PROMPT = (
    "You are an investigative research assistant with expertise in current events "
    "and fact-finding. Your role is to gather accurate information, relevant sources, "
    "and provide comprehensive context for news leads. Focus on finding credible "
    "sources and background information without writing the actual story."
)

# ---------------------------------------------------------------------------
# Research Instructions Template
# ---------------------------------------------------------------------------
RESEARCH_INSTRUCTIONS = (
    "You are tasked with researching a news lead to gather comprehensive background "
    "information and sources. DO NOT write the actual story - only gather facts, "
    "context, and sources that a journalist will use to write the story later.\n\n"
    "Lead:\n{lead_tip}\nDate: {lead_date}\n\n"
    "Research this lead and provide:\n"
    "- A detailed context explaining the background, key players, timeline, and "
    "significance of this lead (200-300 words)\n"
    "- A comprehensive list of credible source URLs that provide information about "
    "this lead\n"
    "- Focus on accuracy, relevance to the {lead_date} timeframe, and providing "
    "multiple perspectives\n"
    "- Include both primary sources (official statements, documents) and secondary "
    "sources (news reports, analysis) where available"
)

# ---------------------------------------------------------------------------
# Research Timeouts and Limits
# ---------------------------------------------------------------------------
RESEARCH_TIMEOUT_SECONDS: int = 240
