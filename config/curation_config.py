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
MIN_SCORE: float = 7.0  # Minimum score for lead consideration
MAX_LEADS: int = 6  # Maximum number of leads to select

# ---------------------------------------------------------------------------
# Evaluation Criteria Weights (must sum to 1.0)
# ---------------------------------------------------------------------------
CRITERIA_WEIGHTS = {
    "impact": 0.25,  # How many people are affected
    "proximity": 0.25,  # Does it cater to a global audience
    "prominence": 0.10,  # Does it involve well-known people
    "relevance": 0.20,  # Is this something the audience cares about
    "hook": 0.10,  # Could this lead grab reader's attention
    "novelty": 0.05,  # Is the story unusual or unexpected
    "conflict": 0.05,  # Is there disagreement, controversy or drama
}

# ---------------------------------------------------------------------------
# Multi-Criteria Evaluation Prompt
# ---------------------------------------------------------------------------

CRITERIA_EVALUATION_SYSTEM_PROMPT = """
You are a senior news editor evaluating discovered news leads for their newsworthiness.

Evaluation Criteria:
• Impact: How many people are affected by this story
• Proximity: Does it cater to a global audience
• Prominence: Does it involve well-known people
• Relevance: Is this something the audience cares about
• Hook: Could this lead grab reader's attention
• Novelty: Is the story unusual or unexpected
• Conflict: Is there disagreement, controversy or drama

Guidelines:
• Rate each criterion on an integer scale from 1 to 10:
  - 1-3: Low (minimal/limited presence of this quality)
  - 4-6: Moderate (noticeable but not exceptional presence)
  - 7-8: High (strong, clear presence of this quality)
  - 9-10: Exceptional (outstanding, rare level of this quality)
• Base every score strictly on the information provided—do NOT assume facts that are not explicitly stated.
• When information is limited, score conservatively based only on what is clearly evident.
• For each lead, first read through all criteria, then score systematically.
• In your brief_reasoning, focus on the most compelling aspect that distinguishes this lead.
""".strip()

CRITERIA_EVALUATION_PROMPT_TEMPLATE = """
Input leads:
{leads_text}
""".strip()

# JSON Schema for structured output
CRITERIA_EVALUATION_SCHEMA = {
    "name": "lead_evaluation",
    "schema": {
        "type": "object",
        "properties": {
            "evaluations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "integer",
                            "minimum": 1
                        },
                        "impact": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "proximity": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "prominence": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "relevance": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "hook": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "novelty": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "conflict": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "brief_reasoning": {
                            "type": "string"
                        }
                    },
                    "required": ["index", "impact", "proximity", "prominence", "relevance", "hook", "novelty", "conflict", "brief_reasoning"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["evaluations"],
        "additionalProperties": False
    }
}