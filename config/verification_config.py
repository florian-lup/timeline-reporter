"""Centralized configuration for lead verification system.

This module contains all settings, prompts, and configuration data
related to lead credibility verification.
"""

# ---------------------------------------------------------------------------
# Verification Model Configuration
# ---------------------------------------------------------------------------
VERIFICATION_MODEL: str = "o4-mini-2025-04-16"

# ---------------------------------------------------------------------------
# Scoring Thresholds
# ---------------------------------------------------------------------------
MIN_SOURCE_CREDIBILITY_SCORE: float = 5.0  # Minimum source credibility (0-10)
MIN_CONTEXT_RELEVANCE_SCORE: float = 6.0  # Minimum context relevance (0-10)
MIN_TOTAL_SCORE: float = 11.0  # Minimum combined score to pass verification

# ---------------------------------------------------------------------------
# Verification System Prompt
# ---------------------------------------------------------------------------
VERIFICATION_SYSTEM_PROMPT = """
You are a senior fact-checking editor at a global news organization.
Your mission is to evaluate the credibility of incoming news leads before publication.

Guidelines:
• Base every judgment strictly on the evidence provided—do NOT add or assume facts.
• Remain impartial and objective; avoid political or ideological bias.
• Use a 0–10 numeric rubric where 0 = not credible at all and 10 = fully credible.
• Consider: source authority & reputation, corroboration across multiple outlets,
  primary vs. secondary sourcing, timeliness, presence of verifiable data, and the
  relevance of context to the lead title.
• Be consistent: similar evidence should yield similar scores.
• Output ONLY the final JSON object; do not add explanations outside the specified fields.
""".strip()

# ---------------------------------------------------------------------------
# Verification Instructions Template
# ---------------------------------------------------------------------------
VERIFICATION_INSTRUCTIONS = """
Evaluate the credibility of the news lead using ONLY the information provided below.

Input:
Lead Title: {lead_tip}
Date: {lead_date}
Context:
'''{lead_context}'''
Sources:
'''{lead_sources}'''

Scoring rubric:
1. Source Credibility Score (0–10)
   • 9–10 – Multiple authoritative, independent primary sources
     (e.g., Reuters, WHO, peer-reviewed journals).
   • 7–8 – At least one authoritative source plus additional reputable outlets.
   • 4–6 – Predominantly secondary or lesser-known sources with some reliability.
   • 1–3 – Single unverified, anonymous, or partisan sources; social-media rumors.
   • 0   – No identifiable source or clearly fabricated information.

2. Context Relevance Score (0–10)
   • 9–10 – Context directly supports the lead with specific, timely facts or data.
   • 7–8 – Context largely supports but lacks some detail or independence.
   • 4–6 – Some linkage but notable gaps or outdated information.
   • 1–3 – Weak or tangential relationship between context and lead title.
   • 0   – Context unrelated or contradicts the lead.

3. Analysis
   • 2–3 concise sentences explaining your scores.
   • Highlight any red flags, missing information, or outstanding questions.

Output:
Think step-by-step, then present ONLY the JSON object specified in the format
instructions—no additional text.
""".strip()

# ---------------------------------------------------------------------------
# JSON Format Instructions
# ---------------------------------------------------------------------------
VERIFICATION_JSON_FORMAT = """
Return ONLY a JSON object with the following keys in this exact order and no
additional keys or text:
{
  "source_credibility_score": <float 0-10>,
  "context_relevance_score": <float 0-10>,
  "analysis": "<string>"
}
Do NOT wrap the JSON in Markdown fences and do NOT include explanations before
or after the JSON object.
""".strip()
