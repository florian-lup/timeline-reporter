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
• Use only publicly available, reputable information. If multiple sources conflict, note the discrepancy.
• Prioritize primary documents (official statements, court filings, scientific papers) and well-established outlets (Reuters, Associated Press, BBC).
• Avoid speculative commentary and opinion pieces unless they are central to the lead—and clearly label them.
• Remain neutral and avoid political or ideological bias.
• Provide an in-depth report (≈ 600–1000 words) detailing relevant background, key actors, chronology, significance, and controversies.
• Supply an array of unique, fully-qualified URLs that support the context. List primary sources first.
• OUTPUT ONLY the JSON object described below—no markdown, headers, or extra commentary.

Expected JSON format (do not include this block in your response):
{
  \"report\": \"<string>\",
  \"sources\": [\"<url1>\", \"<url2>\", ...]
}
""".strip()

# ---------------------------------------------------------------------------
# Research Instructions Template
# ---------------------------------------------------------------------------
RESEARCH_INSTRUCTIONS = """
Research and provide comprehensive background information about the following news lead.

Lead Title: {lead_title}

Provide detailed context, background information, key stakeholders, timeline of events, and significance. Focus on verifiable facts from authoritative sources.
""".strip()

# ---------------------------------------------------------------------------
# Research JSON Format
# ---------------------------------------------------------------------------
RESEARCH_JSON_FORMAT = """
Return ONLY a JSON object with the following keys in this exact order and no additional keys or text:
{
  \"report\": \"<string>\",
  \"sources\": [\"<url1>\", \"<url2>\", ...]
}
Do NOT wrap the JSON in Markdown fences and do NOT include explanations before or after the JSON object.
""".strip()
