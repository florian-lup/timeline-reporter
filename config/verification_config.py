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
VERIFICATION_SYSTEM_PROMPT = (
    "You are a fact-checking expert specializing in evaluating the credibility "
    "and reliability of news leads. Your role is to assess whether a lead is "
    "trustworthy based on its sources and contextual relevance. You provide "
    "objective, numerical scores based on clear criteria."
)

# ---------------------------------------------------------------------------
# Verification Instructions Template
# ---------------------------------------------------------------------------
VERIFICATION_INSTRUCTIONS = (
    "Evaluate the credibility of this news lead based on its sources and context.\n\n"
    "Lead Tip: {lead_tip}\n"
    "Date: {lead_date}\n"
    "Context: {lead_context}\n"
    "Sources: {lead_sources}\n\n"
    "Provide two scores:\n\n"
    "1. Source Credibility Score (0-10):\n"
    "   - Evaluate the quality and reputation of the sources\n"
    "   - Major news networks (CNN, BBC, Reuters, etc.) score 8-10\n"
    "   - Established media outlets score 6-8\n"
    "   - Government/academic sources (.gov, .edu) score 7-9\n"
    "   - Lesser-known but legitimate sources score 4-6\n"
    "   - Blogs, social media, or unverified sources score 0-3\n"
    "   - Consider the diversity and number of sources\n\n"
    "2. Context Relevance Score (0-10):\n"
    "   - How well does the context relate to and support the lead tip?\n"
    "   - Is the information timely and relevant to the {lead_date}?\n"
    "   - Does the context provide substantive, factual information?\n"
    "   - Are there specific details, quotes, or data points?\n\n"
    "3. Analysis:\n"
    "   - Briefly explain your scores\n"
    "   - Note any red flags or credibility concerns\n"
    "   - Identify if this appears to be speculation, rumor, or verified fact"
)

# ---------------------------------------------------------------------------
# JSON Format Instructions
# ---------------------------------------------------------------------------
VERIFICATION_JSON_FORMAT = (
    "\n\nProvide your response as a JSON object with these exact fields:\n"
    "- source_credibility_score: A float between 0 and 10\n"
    "- context_relevance_score: A float between 0 and 10\n"
    "- analysis: A brief explanation (2-3 sentences) of your assessment"
)
