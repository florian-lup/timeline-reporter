"""Lead verification system for credibility checking.

This module verifies the credibility of researched leads based on
source quality and context relevance before they proceed to curation.
"""

from __future__ import annotations

import json

from clients import OpenAIClient
from config.verification_config import (
    MIN_CONTEXT_RELEVANCE_SCORE,
    MIN_SOURCE_CREDIBILITY_SCORE,
    MIN_TOTAL_SCORE,
    VERIFICATION_INSTRUCTIONS,
    VERIFICATION_JSON_FORMAT,
    VERIFICATION_MODEL,
    VERIFICATION_SYSTEM_PROMPT,
)
from models import Lead
from utils import logger

# Maximum length for lead tip display in logs
MAX_TIP_DISPLAY_LENGTH = 50


def verify_leads(leads: list[Lead], *, openai_client: OpenAIClient) -> list[Lead]:
    """Verify lead credibility and filter out unreliable leads.

    Args:
        leads: List of researched leads with context and sources
        openai_client: OpenAI client for GPT-4o verification

    Returns:
        List of verified leads that pass credibility threshold
    """
    verified_leads: list[Lead] = []
    rejected_leads: list[str] = []

    for idx, lead in enumerate(leads, 1):
        first_words = " ".join(lead.tip.split()[:5]) + "..."
        logger.info("  🔎 Verifying lead %d/%d - %s", idx, len(leads), first_words)
        if _verify_lead_credibility(lead, openai_client):
            verified_leads.append(lead)
            logger.info("  ✓ Lead %d/%d passed verification - %s", idx, len(leads), first_words)
        else:
            lead_summary = lead.tip[:MAX_TIP_DISPLAY_LENGTH] + "..." if len(lead.tip) > MAX_TIP_DISPLAY_LENGTH else lead.tip
            rejected_leads.append(lead_summary)
            logger.info(
                "  ✗ Lead %d/%d rejected - %s: %s",
                idx,
                len(leads),
                first_words,
                lead_summary,
            )

    if rejected_leads:
        logger.info("  📊 Rejected %d leads for low credibility", len(rejected_leads))
    else:
        logger.info("  ✓ All leads passed credibility verification")

    return verified_leads


# ---------------------------------------------------------------------------
# Verification Logic
# ---------------------------------------------------------------------------


def _verify_lead_credibility(lead: Lead, openai_client: OpenAIClient) -> bool:
    """Check if a lead meets credibility thresholds.

    Returns:
        True if lead passes verification, False otherwise
    """
    # Get both source credibility and context relevance scores from GPT-4o
    scores = _evaluate_lead_credibility(lead, openai_client)

    if scores is None:
        # Error occurred during evaluation
        return False

    source_score = scores["source_credibility"]
    context_score = scores["context_relevance"]

    # Calculate total score
    total_score = source_score + context_score

    # Check if lead passes all thresholds
    passes_source_threshold = source_score >= MIN_SOURCE_CREDIBILITY_SCORE
    passes_context_threshold = context_score >= MIN_CONTEXT_RELEVANCE_SCORE
    passes_total_threshold = total_score >= MIN_TOTAL_SCORE

    # Log detailed scoring information
    logger.info(
        "    📊 Scores: Source %.1f/%d, Context %.1f/%d, Total %.1f/%d",
        source_score,
        MIN_SOURCE_CREDIBILITY_SCORE,
        context_score,
        MIN_CONTEXT_RELEVANCE_SCORE,
        total_score,
        MIN_TOTAL_SCORE,
    )

    # Determine pass/fail and log the result
    passes_all = passes_source_threshold and passes_context_threshold and passes_total_threshold

    if not passes_all:
        failed_criteria = []
        if not passes_source_threshold:
            failed_criteria.append(f"source credibility ({source_score:.1f} < {MIN_SOURCE_CREDIBILITY_SCORE})")
        if not passes_context_threshold:
            failed_criteria.append(f"context relevance ({context_score:.1f} < {MIN_CONTEXT_RELEVANCE_SCORE})")
        if not passes_total_threshold:
            failed_criteria.append(f"total score ({total_score:.1f} < {MIN_TOTAL_SCORE})")

        logger.info("    ❌ Failed: %s", ", ".join(failed_criteria))
    else:
        logger.info("    ✅ Passed: All credibility thresholds met")

    return passes_all


def _evaluate_lead_credibility(lead: Lead, openai_client: OpenAIClient) -> dict[str, float] | None:
    """Use GPT-4o to evaluate both source credibility and context relevance.

    Args:
        lead: Lead with tip, context, and sources
        openai_client: OpenAI client

    Returns:
        Dictionary with 'source_credibility' and 'context_relevance' scores,
        or None if evaluation fails
    """
    # Format sources for the prompt
    sources_text = "\n".join(f"- {source}" for source in lead.sources) if lead.sources else "No sources provided"

    # Create the verification prompt
    prompt = VERIFICATION_INSTRUCTIONS.format(
        lead_tip=lead.tip,
        lead_date=lead.date,
        lead_context=lead.context,
        lead_sources=sources_text,
    )

    # Add JSON format instructions
    full_prompt = VERIFICATION_SYSTEM_PROMPT + "\n\n" + prompt + VERIFICATION_JSON_FORMAT

    try:
        # Get GPT-4o evaluation
        response = openai_client.chat_completion(
            prompt=full_prompt,
            model=VERIFICATION_MODEL,
            response_format={"type": "json_object"},
        )

        # Parse the JSON response
        evaluation = json.loads(response)

        # Extract scores
        source_score = float(evaluation.get("source_credibility_score", 0))
        context_score = float(evaluation.get("context_relevance_score", 0))
        analysis = evaluation.get("analysis", "")

        # Log the analysis
        logger.debug("Verification analysis: %s", analysis)

        # Ensure scores are within valid range
        return {
            "source_credibility": max(0.0, min(10.0, source_score)),
            "context_relevance": max(0.0, min(10.0, context_score)),
        }

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error("Error parsing verification response: %s", e)
        return None
    except Exception as e:
        logger.error("Error during credibility evaluation: %s", e)
        return None
