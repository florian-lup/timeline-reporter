"""Centralized configuration for lead curation system.

This module contains all settings, prompts, and configuration data
related to lead curation and evaluation.
"""

# ---------------------------------------------------------------------------
# Curation Model Configuration
# ---------------------------------------------------------------------------
CURATION_MODEL: str = "o3-2025-04-16"

# ---------------------------------------------------------------------------
# Lead Selection Parameters
# ---------------------------------------------------------------------------
MIN_WEIGHTED_SCORE: float = 7.0  # Minimum score for lead consideration
MAX_LEADS: int = 6  # Maximum number of leads to select
MIN_LEADS: int = 4  # Minimum number of leads to select

# ---------------------------------------------------------------------------
# Evaluation Criteria Weights (must sum to 1.0)
# ---------------------------------------------------------------------------
CRITERIA_WEIGHTS = {
    "impact": 0.20,  # How many people are affected
    "proximity": 0.15,  # Does it cater to a global audience
    "prominence": 0.15,  # Does it involve well-known people
    "relevance": 0.15,  # Is this something the audience cares about
    "hook": 0.15,  # Could this lead grab reader's attention
    "novelty": 0.10,  # Is the story unusual or unexpected
    "conflict": 0.10,  # Is there disagreement, controversy or drama
}

# ---------------------------------------------------------------------------
# Multi-Criteria Evaluation Prompt
# ---------------------------------------------------------------------------

CRITERIA_EVALUATION_SYSTEM_PROMPT = """
You are a senior news editor evaluating discovered news leads for their newsworthiness.

Guidelines:
• Rate each criterion on an integer scale from 1 (very low) to 10 (exceptionally high).
• Base every score strictly on the information provided—do NOT assume facts that are not explicitly stated.
• Apply the same standard across all leads so that similar qualities yield similar scores.
• After scoring, include a one-sentence 'brief_reasoning' highlighting the key factor driving your evaluation.

Output requirement:
Think step-by-step, then return ONLY the JSON object with exactly the following structure and no additional keys or commentary:
{
  "evaluations": [
    {
      "index": <int>,
      "impact": <int 1-10>,
      "proximity": <int 1-10>,
      "prominence": <int 1-10>,
      "relevance": <int 1-10>,
      "hook": <int 1-10>,
      "novelty": <int 1-10>,
      "conflict": <int 1-10>,
      "brief_reasoning": "<string>"
    }
  ]
}
Do NOT wrap the JSON in Markdown fences and do NOT add explanations before or after the JSON object.
""".strip()

CRITERIA_EVALUATION_PROMPT_TEMPLATE = """
Input leads:
{leads_text}
""".strip()
