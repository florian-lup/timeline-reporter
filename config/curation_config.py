"""Centralized configuration for lead curation system.

This module contains all settings, prompts, and configuration data
related to lead curation and evaluation.
"""


# ---------------------------------------------------------------------------
# Curation Model Configuration
# ---------------------------------------------------------------------------
CURATION_MODEL: str = "o4-mini-2025-04-16"

# ---------------------------------------------------------------------------
# Lead Selection Parameters
# ---------------------------------------------------------------------------
MIN_WEIGHTED_SCORE: float = 6.0  # Minimum score for lead consideration
MAX_LEADS: int = 5  # Maximum number of leads to select
MIN_LEADS: int = 3  # Minimum number of leads to select
SCORE_SIMILARITY: float = 0.5  # Score threshold for pairwise comparison

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
# Pairwise Comparison Configuration
# ---------------------------------------------------------------------------
MIN_GROUP_SIZE_FOR_PAIRWISE: int = 2  # Minimum leads needed for pairwise comparison

# ---------------------------------------------------------------------------
# Final Ranking Weights
# ---------------------------------------------------------------------------
WEIGHTED_SCORE_WEIGHT: float = 0.7  # Weight for criteria-based score
PAIRWISE_SCORE_WEIGHT: float = 0.3  # Weight for pairwise comparison results

# ---------------------------------------------------------------------------
# Decision/Curation System Prompts
# ---------------------------------------------------------------------------

CURATION_SYSTEM_PROMPT = (
    "You are an expert news editor with decades of experience in editorial "
    "decision-making. Your role is to evaluate and prioritize news events "
    "based on their impact, significance, and newsworthiness. Focus on "
    "quality over quantity, selecting only the most important stories that "
    "deserve in-depth coverage."
)

CURATION_INSTRUCTIONS = (
    "Below are deduplicated news leads discovered today. Your task is to "
    "select the most impactful stories.\n\nLeads to evaluate:\n{leads}\n\n"
    "Evaluation criteria (in order of importance):\n"
    "1. Global impact and significance\n"
    "2. Potential long-term consequences\n"
    "3. Public interest and relevance\n"
    "4. Uniqueness and newsworthiness\n"
    "5. Credibility and verifiability\n\n"
    "Select the top 3-5 most impactful events that warrant comprehensive "
    "research and reporting.\n\n"
    "Return only the numbers of the events you want to keep "
    '(e.g., "1, 3, 5" or "2, 4, 7").\n'
    "Focus on stories that will have the greatest impact on your audience "
    "and society."
)

# ---------------------------------------------------------------------------
# Multi-Criteria Evaluation Prompt
# ---------------------------------------------------------------------------

CRITERIA_EVALUATION_PROMPT_TEMPLATE = (
    """You are evaluating news leads for their newsworthiness using """
    """specific journalistic criteria.

Evaluate each lead on these criteria (1-10 scale):

1. Impact: How many people are affected? (1=few individuals, 10=millions globally)
2. Proximity: Does it cater to a global audience?
   (1=hyper-local interest only, 10=universally relevant)
3. Prominence: Does it involve well-known people?
   (1=unknown individuals, 10=world leaders/A-list celebrities)
4. Relevance: Is this something the audience cares about?
   (1=obscure topic, 10=hot-button issue everyone discusses)
5. Hook: Could this lead grab reader's attention?
   (1=boring/predictable, 10=instantly compelling)
6. Novelty: Is the story unusual or unexpected?
   (1=routine occurrence, 10=unprecedented/shocking)
7. Conflict: Is there disagreement, controversy or drama?
   (1=harmonious/consensual, 10=major dispute/scandal)

Leads to evaluate:
{leads_text}

Return a JSON array with scores for each lead:
[{{
    "index": 1,
    "impact": 8,
    "proximity": 7,
    "prominence": 6,
    "relevance": 9,
    "hook": 8,
    "novelty": 5,
    "conflict": 7,
    "brief_reasoning": "Major event affecting millions with global implications..."
}}]"""
)

# ---------------------------------------------------------------------------
# Pairwise Comparison Prompt Template
# ---------------------------------------------------------------------------

PAIRWISE_COMPARISON_PROMPT_TEMPLATE = (
    """For each pair of leads below, determine which is more newsworthy """
    """and impactful.
Consider all evaluation criteria but focus on real-world impact and reader interest.

{comparisons_text}

Return a JSON array with your decisions:
[{{"pair": "1vs2", "winner": 1, "confidence": "high",
  "reason": "Lead A has broader global impact"}}]

Note: winner should be either the first or second number from the pair."""
)

# ---------------------------------------------------------------------------
# Prompt Collections for Easy Access
# ---------------------------------------------------------------------------

DECISION_PROMPTS = {
    "system": CURATION_SYSTEM_PROMPT,
    "instructions": CURATION_INSTRUCTIONS,
}

CURATION_PROMPTS = {
    "decision": DECISION_PROMPTS,
    "criteria_evaluation": CRITERIA_EVALUATION_PROMPT_TEMPLATE,
    "pairwise_comparison": PAIRWISE_COMPARISON_PROMPT_TEMPLATE,
}

# All curation prompts for easy iteration/management
ALL_CURATION_PROMPTS = {
    "decision": DECISION_PROMPTS,
    "criteria_evaluation": CRITERIA_EVALUATION_PROMPT_TEMPLATE,
    "pairwise_comparison": PAIRWISE_COMPARISON_PROMPT_TEMPLATE,
}
