"""Centralized configuration for lead verification system.

This module contains all settings, prompts, and configuration data
related to lead credibility verification using GPT-4o.
"""

# ---------------------------------------------------------------------------
# Verification Model Configuration
# ---------------------------------------------------------------------------
VERIFICATION_MODEL: str = "gpt-4o"
VERIFICATION_TEMPERATURE: float = 0.2  # Low temperature for consistent scoring

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
You are a fact-checking expert specializing in evaluating the credibility
and reliability of news leads. Your role is to assess whether a lead is
trustworthy based on its sources and contextual relevance. You provide
objective, numerical scores based on clear criteria.
""".strip()

# ---------------------------------------------------------------------------
# Verification Instructions Template
# ---------------------------------------------------------------------------
VERIFICATION_INSTRUCTIONS = """
Evaluate the credibility of this news lead based on its sources and context.

Lead Tip: {lead_tip}
Date: {lead_date}
Context: {lead_context}
Sources: {lead_sources}

Provide two scores:

1. Source Credibility Score (0-10):
   - Evaluate the quality and reputation of the sources
   - Major news networks (CNN, BBC, Reuters, etc.) score 8-10
   - Established media outlets score 6-8
   - Government/academic sources (.gov, .edu) score 7-9
   - Lesser-known but legitimate sources score 4-6
   - Blogs, social media, or unverified sources score 0-3
   - Consider the diversity and number of sources

2. Context Relevance Score (0-10):
   - How well does the context relate to and support the lead tip?
   - Is the information timely and relevant to the {lead_date}?
   - Does the context provide substantive, factual information?
   - Are there specific details, quotes, or data points?

3. Analysis:
   - Briefly explain your scores
   - Note any red flags or credibility concerns
   - Identify if this appears to be speculation, rumor, or verified fact
""".strip()

# ---------------------------------------------------------------------------
# JSON Format Instructions
# ---------------------------------------------------------------------------
VERIFICATION_JSON_FORMAT = """

Provide your response as a JSON object with these exact fields:
- source_credibility_score: A float between 0 and 10
- context_relevance_score: A float between 0 and 10
- analysis: A brief explanation (2-3 sentences) of your assessment
""".strip()
