from __future__ import annotations

import re

from clients import OpenAIClient
from config import DECISION_INSTRUCTIONS, DECISION_SYSTEM_PROMPT
from config.settings import DECISION_MODEL
from models import Lead
from utils import logger


def select_events(events: list[Lead], *, openai_client: OpenAIClient) -> list[Lead]:
    """Selects the most impactful events from deduplicated list.

    Uses AI to evaluate events based on impact, significance, and newsworthiness,
    returning only the top priority stories that warrant comprehensive research.
    """
    if not events:
        logger.info("No events to evaluate")
        return []

    logger.info("Evaluating %d events for priority", len(events))

    # Format events for evaluation with numbers
    events_text = "\n".join(
        [
            f"{i + 1}. Title: {event.title}\n   Summary: {event.summary}\n"
            for i, event in enumerate(events)
        ]
    )

    # Create decision prompt
    full_prompt = (
        f"{DECISION_SYSTEM_PROMPT}\n\n"
        f"{DECISION_INSTRUCTIONS.format(events=events_text)}"
    )

    # Get AI decision on most impactful events using decision model
    response_text = openai_client.chat_completion(
        full_prompt,
        model=DECISION_MODEL,
    )

    # Parse the selected event indices and filter original events
    selected_events = _filter_events_by_indices(response_text, events)

    logger.info("Selected %d priority events", len(selected_events))

    # Log the selected events for transparency
    for i, event in enumerate(selected_events, 1):
        logger.info("Priority %d: %s", i, event.title)

    return selected_events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _filter_events_by_indices(
    response_text: str, original_events: list[Lead]
) -> list[Lead]:
    """Filters original events based on selected indices from AI response."""
    # Extract numbers from response (handles formats like "1, 3, 5" or "2 4 7" etc.)
    numbers = re.findall(r"\b(\d+)\b", response_text)

    if not numbers:
        logger.warning("No valid numbers in response, using fallback")
        return original_events[:3]

    selected_events = []

    for num_str in numbers:
        try:
            # Convert to 0-based index
            index = int(num_str) - 1

            # Check if index is valid
            if 0 <= index < len(original_events):
                event = original_events[index]
                selected_events.append(event)
            else:
                logger.warning(
                    "Invalid event number %s (max: %d)", num_str, len(original_events)
                )

        except ValueError:
            logger.warning("Could not parse number: %s", num_str)
            continue

    # Ensure we don't return empty list due to parsing issues
    if not selected_events and original_events:
        logger.warning("No valid selections, using top 3 fallback")
        return original_events[:3]

    return selected_events
