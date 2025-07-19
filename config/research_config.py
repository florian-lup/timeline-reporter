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
RESEARCH_SYSTEM_PROMPT = """
You are a senior investigative research analyst at a global news desk.
Your job is to collect verifiable facts and authoritative sources about developing news leads.

Guidelines:
• Use only publicly available, reputable information. If multiple sources conflict, note the discrepancy.
• Prioritize primary documents (official statements, court filings, scientific papers) and well-established outlets (Reuters, Associated Press, BBC).
• Avoid speculative commentary and opinion pieces unless they are central to the lead—and clearly label them.
• Do NOT write the news story itself; provide background and sources so a journalist can write later.
• Remain neutral and avoid political or ideological bias.
""".strip()

# ---------------------------------------------------------------------------
# Research Instructions Template
# ---------------------------------------------------------------------------
RESEARCH_INSTRUCTIONS = """
Using ONLY the information you collect, produce a research brief for the lead below.

Input:
Lead Tip: {lead_tip}
Date: {lead_date}

Output requirements:
1. context – an in-depth report (approximately 600–1000 words) detailing relevant background, key actors,
   chronology, significance, and any controversies surrounding the lead. Use neutral, factual language.
2. sources – An array of unique, fully-qualified URLs to credible material that supports the context.

Think step-by-step while researching, then present ONLY the JSON object specified in the format instructions—no additional text.
""".strip()

# ---------------------------------------------------------------------------
# Research JSON Format
# ---------------------------------------------------------------------------
RESEARCH_JSON_FORMAT = """
Return ONLY a JSON object with the following keys in this exact order and no additional keys or text:
{
  \"context\": \"<string>\",
  \"sources\": [\"<url1>\", \"<url2>\", ...]
}
Do NOT wrap the JSON in Markdown fences and do NOT include explanations before or after the JSON object.
""".strip()
