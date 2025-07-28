"""Lead curation system combining multiple evaluation techniques."""

from __future__ import annotations

import json
from dataclasses import dataclass

from clients import OpenAIClient
from config.curation_config import (
    CRITERIA_EVALUATION_PROMPT_TEMPLATE,
    CRITERIA_EVALUATION_SYSTEM_PROMPT,
    CRITERIA_WEIGHTS,
    CURATION_MODEL,
    MAX_LEADS,
    MIN_LEADS,
    MIN_WEIGHTED_SCORE,
)
from models import Lead, LeadEvaluation
from utils import logger

# Constants for magic values
MAX_REASONING_DISPLAY_LENGTH = 80


class LeadCurator:
    """Advanced lead curation using multiple evaluation techniques."""

    def __init__(self, openai_client: OpenAIClient):
        """Initialize the curator with an OpenAI client."""
        self.openai_client = openai_client

    def curate_leads(self, leads: list[Lead]) -> list[Lead]:
        """Main entry point for curation."""
        if not leads:
            return []

        logger.info("  ⚖️ Analyzing %d leads using multi-criteria evaluation...", len(leads))

        # Step 1: Multi-criteria evaluation
        evaluations = self._evaluate_all_criteria(leads)

        # Step 2: Filter by minimum threshold
        qualified = [e for e in evaluations if e.weighted_score >= MIN_WEIGHTED_SCORE]
        failed_threshold = [e for e in evaluations if e.weighted_score < MIN_WEIGHTED_SCORE]

        logger.info(
            "  📊 Threshold analysis: %d/%d leads passed minimum score requirement (%.1f)",
            len(qualified),
            len(leads),
            MIN_WEIGHTED_SCORE,
        )

        if failed_threshold:
            logger.info(
                "  📉 %d leads below threshold: scores %.1f-%.1f",
                len(failed_threshold),
                min(e.weighted_score for e in failed_threshold),
                max(e.weighted_score for e in failed_threshold),
            )

        if not qualified:
            # No leads passed threshold - return empty list
            logger.warning(
                "No leads passed minimum threshold (%.2f), returning empty list",
                MIN_WEIGHTED_SCORE,
            )
            return []

        # Step 3: Final ranking based on weighted scores
        final_ranking = self._compute_final_ranking(qualified)

        # Step 4: Select top leads by final rank
        selected = self._select_top_leads(final_ranking)

        logger.info(
            "  ✓ Priority selection complete: %d high-impact leads selected",
            len(selected),
        )

        # Log the final selected leads with their scores
        for i, evaluation in enumerate(selected, 1):
            first_words = " ".join(evaluation.lead.discovered_lead.split()[:5]) + "..."
            logger.info(
                "  🏆 Selected #%d: Score %.1f - %s",
                i,
                evaluation.weighted_score,
                first_words,
            )
        return [e.lead for e in selected]

    def _evaluate_all_criteria(self, leads: list[Lead]) -> list[LeadEvaluation]:
        """Step 1: Evaluate each lead on multiple criteria."""
        # Format leads for evaluation using discovered lead text
        leads_text = "\n".join(f"{i + 1}. {lead.discovered_lead}" for i, lead in enumerate(leads))

        # Use system prompt with user message containing the leads
        user_prompt = CRITERIA_EVALUATION_PROMPT_TEMPLATE.format(leads_text=leads_text)

        response_text = self.openai_client.chat_completion(
            user_prompt, 
            model=CURATION_MODEL, 
            response_format={"type": "json_object"},
            system_prompt=CRITERIA_EVALUATION_SYSTEM_PROMPT
        )

        # Parse response
        try:
            scores_data = json.loads(response_text)

            # Handle both object with 'evaluations' array and direct array
            if isinstance(scores_data, dict) and "evaluations" in scores_data:
                scores_data = scores_data["evaluations"]
            elif isinstance(scores_data, dict):
                # If it's a dict but not with 'evaluations', try to extract array
                # Look for any key that contains a list
                for value in scores_data.values():
                    if isinstance(value, list):
                        scores_data = value
                        break
                else:
                    raise ValueError("No array found in response")

            # Ensure scores_data is a list
            if not isinstance(scores_data, list):
                raise ValueError(f"Expected list, got {type(scores_data)}")

        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("Failed to parse JSON response: %s", exc)
            raise ValueError(f"Failed to parse criteria evaluation response: {exc}") from exc

        evaluations = []
        for i, lead in enumerate(leads):
            # Find scores for this lead
            lead_scores = None
            for score_entry in scores_data:
                if score_entry.get("index") == i + 1:
                    lead_scores = score_entry
                    break

            if not lead_scores:
                raise ValueError(f"No scores found for lead {i + 1}")

            # Check for missing criteria first
            missing_criteria = [k for k in CRITERIA_WEIGHTS if k not in lead_scores]
            if missing_criteria:
                raise ValueError(
                    f"Lead {i + 1} missing required criteria scores: {missing_criteria}"
                )

            criteria_scores = {
                k: float(lead_scores[k]) for k in CRITERIA_WEIGHTS
            }

            # Calculate weighted score
            weighted = sum(score * CRITERIA_WEIGHTS[criterion] for criterion, score in criteria_scores.items())

            evaluations.append(
                LeadEvaluation(
                    lead=lead,
                    criteria_scores=criteria_scores,
                    weighted_score=weighted,
                )
            )

            first_words = " ".join(lead.discovered_lead.split()[:5]) + "..."
            reasoning = lead_scores.get("brief_reasoning", "No reasoning provided")
            reasoning_display = reasoning[:MAX_REASONING_DISPLAY_LENGTH] + ("..." if len(reasoning) > MAX_REASONING_DISPLAY_LENGTH else "")
            logger.info(
                "  📊 Lead %d/%d scored %.1f - %s: %s",
                i + 1,
                len(leads),
                weighted,
                first_words,
                reasoning_display,
            )

        return evaluations

    def _compute_final_ranking(self, evaluations: list[LeadEvaluation]) -> list[LeadEvaluation]:
        """Step 3: Rank leads based on weighted scores."""
        # Final rank is simply the weighted score
        for eval in evaluations:
            eval.final_rank = eval.weighted_score
            
            logger.debug(
                "Lead final ranking: weighted=%.2f, final=%.2f",
                eval.weighted_score,
                eval.final_rank,
            )

        # Sort by final rank
        evaluations.sort(key=lambda x: x.final_rank, reverse=True)

        return evaluations

    def _select_top_leads(self, ranked_evaluations: list[LeadEvaluation]) -> list[LeadEvaluation]:
        """Step 4: Select top leads by final rank."""
        # Simply take the top N leads based on final ranking
        selected = ranked_evaluations[: MAX_LEADS]

        # Ensure minimum selection
        if len(selected) < MIN_LEADS and len(ranked_evaluations) >= MIN_LEADS:
            selected = ranked_evaluations[: MIN_LEADS]

        return selected


def curate_leads(leads: list[Lead], *, openai_client: OpenAIClient) -> list[Lead]:
    """Selects the most impactful leads from deduplicated list.

    Uses AI evaluation with multi-criteria scoring to select only 
    the top priority stories that warrant comprehensive research.
    """
    if not leads:
        logger.info("  ⚠️ No leads to evaluate")
        return []

    # Use the curation system
    curator = LeadCurator(openai_client)
    return curator.curate_leads(leads)
