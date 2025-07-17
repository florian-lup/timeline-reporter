from __future__ import annotations

import re

from clients import OpenAIClient
from config import DECISION_INSTRUCTIONS, DECISION_SYSTEM_PROMPT
from config.settings import DECISION_MODEL
from models import Lead
from utils import logger

# Constants
CONTEXT_PREVIEW_LENGTH = 50


def curate_leads(leads: list[Lead], *, openai_client: OpenAIClient) -> list[Lead]:
    """Selects the most impactful leads from deduplicated list.

    Uses AI to evaluate leads based on impact, significance, and newsworthiness,
    returning only the top priority stories that warrant comprehensive research.
    """
    if not leads:
        logger.info("No leads to evaluate")
        return []

    logger.info("Evaluating %d leads for priority", len(leads))

    # Format leads for evaluation with numbers
    leads_text = "\n".join(
        [f"{i + 1}. {lead.context}\n" for i, lead in enumerate(leads)]
    )

    # Create decision prompt
    full_prompt = (
        f"{DECISION_SYSTEM_PROMPT}\n\n{DECISION_INSTRUCTIONS.format(leads=leads_text)}"
    )

    # Get AI decision on most impactful leads using decision model
    response_text = openai_client.chat_completion(
        full_prompt,
        model=DECISION_MODEL,
    )

    # Parse the selected lead indices and filter original leads
    selected_leads = _filter_leads_by_indices(response_text, leads)

    logger.info("Selected %d priority leads", len(selected_leads))

    # Log the selected leads for transparency
    for i, lead in enumerate(selected_leads, 1):
        context_preview = (
            lead.context[:CONTEXT_PREVIEW_LENGTH] + "..."
            if len(lead.context) > CONTEXT_PREVIEW_LENGTH
            else lead.context
        )
        logger.info("Priority %d: %s", i, context_preview)

    return selected_leads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _filter_leads_by_indices(
    response_text: str, original_leads: list[Lead]
) -> list[Lead]:
    """Filters original leads based on selected indices from AI response."""
    # Extract numbers from response (handles formats like "1, 3, 5" or "2 4 7" etc.)
    numbers = re.findall(r"\b(\d+)\b", response_text)

    if not numbers:
        logger.warning("No valid numbers in response, using fallback")
        return original_leads[:3]

    selected_leads = []

    for num_str in numbers:
        try:
            # Convert to 0-based index
            index = int(num_str) - 1

            # Check if index is valid
            if 0 <= index < len(original_leads):
                lead = original_leads[index]
                selected_leads.append(lead)
            else:
                logger.warning(
                    "Invalid lead number %s (max: %d)", num_str, len(original_leads)
                )

        except ValueError:
            logger.warning("Could not parse number: %s", num_str)
            continue

    # Ensure we don't return empty list due to parsing issues
    if not selected_leads and original_leads:
        logger.warning("No valid selections, using top 3 fallback")
        return original_leads[:3]

    return selected_leads
