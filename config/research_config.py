"""Centralized configuration for lead research system.

This module contains all settings, prompts, and configuration data
related to lead research and source gathering.
"""

# ---------------------------------------------------------------------------
# Query Formulation Configuration
# ---------------------------------------------------------------------------
QUERY_FORMULATION_MODEL: str = "o4-mini-2025-04-16"

# ---------------------------------------------------------------------------
# Query Formulation System Prompt
# ---------------------------------------------------------------------------
QUERY_FORMULATION_SYSTEM_PROMPT = """
You are an expert research strategist who specializes in formulating effective search queries.
Your job is to transform raw news titles into precise, actionable search queries that will help
researchers find relevant background information and sources.

Guidelines:
• Identify the key entities, events, and concepts in the title.
• Include an explicit time filter when appropriate (e.g., "past 24 hours") to improve relevance.
• Anticipate authoritative sources that might surface (official statements, government releases, established outlets).
• Keep queries concise yet comprehensive enough to capture the essential elements—avoid overly generic terms.
• Focus on factual, verifiable information; avoid words that prompt speculation (e.g., "rumor", "opinion").
""".strip()

# ---------------------------------------------------------------------------
# Query Formulation Instructions Template
# ---------------------------------------------------------------------------
QUERY_FORMULATION_INSTRUCTIONS = (
    "Transform the news title below into ONE optimized search query that will surface "
    "authoritative background, recent developments, and any useful historical context. "
    "If timeliness is critical, append an appropriate date/time filter "
    "(e.g., 'past 24 hours', '2025').\n\n"
    "Lead Title: {lead_tip}\n"
    "Date: {lead_date}\n\n"
    "Return ONLY the search query—no additional text, explanation, or formatting."
).strip()

# ---------------------------------------------------------------------------
# Research Model Configuration
# ---------------------------------------------------------------------------
LEAD_RESEARCH_MODEL: str = "sonar-pro"
SEARCH_CONTEXT_SIZE: str = "high"

# ---------------------------------------------------------------------------
# Research Timeout Configuration  
# ---------------------------------------------------------------------------
RESEARCH_TIMEOUT_SECONDS: float = 90  # Total timeout for research operations

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
  \"context\": \"<string>\",
  \"sources\": [\"<url1>\", \"<url2>\", ...]
}
""".strip()

# ---------------------------------------------------------------------------
# Research Instructions Template
# ---------------------------------------------------------------------------
RESEARCH_INSTRUCTIONS = """{search_query}""".strip()

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
