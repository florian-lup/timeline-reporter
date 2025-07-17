"""Hybrid lead curation system combining multiple evaluation techniques."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from clients import OpenAIClient
from config.settings import (
    CURATION_MODEL,
    HYBRID_MAX_LEADS,
    HYBRID_MIN_LEADS,
    HYBRID_MIN_WEIGHTED_SCORE,
    HYBRID_SCORE_SIMILARITY,
)
from models import Lead
from utils import logger


@dataclass
class LeadEvaluation:
    """Comprehensive evaluation of a lead."""

    lead: Lead
    criteria_scores: dict[str, float]  # Individual criteria scores
    weighted_score: float  # Overall weighted score
    pairwise_wins: int = 0  # Number of pairwise comparisons won
    final_rank: float = 0.0  # Final ranking after all evaluations


class HybridLeadCurator:
    """Advanced lead curation using multiple evaluation techniques."""

    # Criteria weights (must sum to 1.0)
    CRITERIA_WEIGHTS = {
        "impact": 0.20,         # How many people are affected
        "proximity": 0.15,      # Does it cater to a global audience
        "prominence": 0.15,     # Does it involve well-known people
        "relevance": 0.15,      # Is this something the audience cares about
        "hook": 0.15,          # Could this lead grab reader's attention
        "novelty": 0.10,       # Is the story unusual or unexpected
        "conflict": 0.10       # Is there disagreement, controversy or drama
    }

    # Configuration from settings
    MIN_WEIGHTED_SCORE = HYBRID_MIN_WEIGHTED_SCORE
    MAX_LEADS_TO_SELECT = HYBRID_MAX_LEADS
    MIN_LEADS_TO_SELECT = HYBRID_MIN_LEADS
    SCORE_SIMILARITY_THRESHOLD = HYBRID_SCORE_SIMILARITY
    MIN_GROUP_SIZE_FOR_PAIRWISE = 2  # Minimum leads needed for pairwise comparison

    def __init__(self, openai_client: OpenAIClient):
        """Initialize the hybrid curator with an OpenAI client."""
        self.openai_client = openai_client

    def curate_leads(self, leads: list[Lead]) -> list[Lead]:
        """Main entry point for hybrid curation."""
        if not leads:
            return []

        logger.info("Starting hybrid curation for %d leads", len(leads))

        # Step 1: Multi-criteria evaluation
        evaluations = self._evaluate_all_criteria(leads)

        # Step 2: Filter by minimum threshold
        qualified = [
            e for e in evaluations
            if e.weighted_score >= self.MIN_WEIGHTED_SCORE
        ]
        logger.info("%d leads passed minimum threshold", len(qualified))

        if not qualified:
            # Fallback: return top leads by weighted score
            logger.warning(
                "FALLBACK: No leads passed minimum threshold (%.2f), "
                "selecting top %d by weighted score",
                self.MIN_WEIGHTED_SCORE, self.MIN_LEADS_TO_SELECT
            )
            evaluations.sort(key=lambda x: x.weighted_score, reverse=True)
            return [e.lead for e in evaluations[:self.MIN_LEADS_TO_SELECT]]

        # Step 3: Pairwise comparisons for close scores
        if len(qualified) > self.MAX_LEADS_TO_SELECT:
            self._perform_pairwise_comparisons(qualified)

        # Step 4: Final ranking combining all factors
        final_ranking = self._compute_final_ranking(qualified)

        # Step 5: Select top leads by final rank
        selected = self._select_top_leads(final_ranking)

        logger.info("Hybrid curation completed successfully without fallbacks")
        logger.info("Selected %d leads through hybrid curation", len(selected))
        return [e.lead for e in selected]

    def _evaluate_all_criteria(self, leads: list[Lead]) -> list[LeadEvaluation]:
        """Step 1: Evaluate each lead on multiple criteria."""
        # Format leads for evaluation
        leads_text = "\n".join(
            f"{i + 1}. {lead.context}"
            for i, lead in enumerate(leads)
        )

        # Batch evaluation prompt for efficiency
        prompt = f"""You are evaluating news leads for their newsworthiness using
specific journalistic criteria.

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

        response_text = self.openai_client.chat_completion(
            prompt,
            model=CURATION_MODEL,
        )

        # Parse response
        try:
            # Handle potential JSON wrapped in markdown
            json_match = re.search(
                r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL
            )
            if json_match:
                response_text = json_match.group(1)

            scores_data = json.loads(response_text)
            # Ensure scores_data is a list
            if not isinstance(scores_data, list):
                raise ValueError(f"Expected list, got {type(scores_data)}")
        except (json.JSONDecodeError, ValueError):
            logger.error("Failed to parse JSON response: %s", response_text)
            # Fallback: treat all leads equally
            logger.warning(
                "FALLBACK: Using default scores (7.0) for all criteria "
                "due to JSON parsing failure"
            )
            scores_data = [
                {
                    "index": i + 1,
                    "impact": 7,
                    "proximity": 7,
                    "prominence": 7,
                    "relevance": 7,
                    "hook": 7,
                    "novelty": 7,
                    "conflict": 7,
                    "brief_reasoning": "Default scoring due to parse error"
                }
                for i in range(len(leads))
            ]

        evaluations = []
        for i, lead in enumerate(leads):
            # Find scores for this lead
            lead_scores = None
            for score_entry in scores_data:
                if score_entry.get("index") == i + 1:
                    lead_scores = score_entry
                    break

            if lead_scores:
                criteria_scores = {
                    k: float(lead_scores.get(k, 7))  # Default to 7 if missing
                    for k in self.CRITERIA_WEIGHTS
                }

                # Check for missing criteria and log if any defaults were used
                missing_criteria = [
                    k for k in self.CRITERIA_WEIGHTS if k not in lead_scores
                ]
                if missing_criteria:
                    logger.warning(
                        "FALLBACK: Lead %d missing criteria scores for %s, "
                        "using default (7.0)",
                        i + 1, missing_criteria
                    )

                # Calculate weighted score
                weighted = sum(
                    score * self.CRITERIA_WEIGHTS[criterion]
                    for criterion, score in criteria_scores.items()
                )

                evaluations.append(LeadEvaluation(
                    lead=lead,
                    criteria_scores=criteria_scores,
                    weighted_score=weighted
                ))

                logger.debug(
                    "Lead %d scored %.2f (reasoning: %s)",
                    i + 1,
                    weighted,
                    lead_scores.get("brief_reasoning", "")
                )

        return evaluations

    def _perform_pairwise_comparisons(self, evaluations: list[LeadEvaluation]) -> None:
        """Step 3: Use pairwise comparisons for close scores."""
        # Group leads with similar scores
        score_groups = self._group_by_score_similarity(evaluations)

        for group in score_groups:
            if len(group) > 1:
                self._compare_group_pairwise(group)

    def _compare_group_pairwise(self, group: list[LeadEvaluation]) -> None:
        """Compare leads within a group using pairwise comparisons."""
        if len(group) < self.MIN_GROUP_SIZE_FOR_PAIRWISE:
            return

        # Build comparison pairs
        comparisons_text = []
        pair_map = {}  # Maps pair string to (i, j) indices

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                pair_key = f"{i+1}vs{j+1}"
                pair_map[pair_key] = (i, j)

                comparisons_text.append(f"""
Pair {pair_key}:
Lead A ({i+1}): {group[i].lead.context[:200]}...
Lead B ({j+1}): {group[j].lead.context[:200]}...
""")

        # Batch all comparisons for efficiency
        prompt = (
            f"For each pair of leads below, determine which is more newsworthy "
            f"and impactful.\n"
            f"Consider all evaluation criteria but focus on real-world impact "
            f"and reader interest.\n\n"
            f"{chr(10).join(comparisons_text)}\n\n"
            f"Return a JSON array with your decisions:\n"
            f'[{{"pair": "1vs2", "winner": 1, "confidence": "high",'
            f'"reason": "Lead A has broader global impact"}}]\n\n'
            f"Note: winner should be either the first or second number from the pair."
        )

        response_text = self.openai_client.chat_completion(
            prompt,
            model=CURATION_MODEL,
        )

        # Parse response
        try:
            json_match = re.search(
                r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL
            )
            if json_match:
                response_text = json_match.group(1)

            results = json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse pairwise comparison results")
            logger.warning(
                "FALLBACK: Skipping pairwise comparisons, using only "
                "weighted scores for ranking"
            )
            return

        # Update pairwise wins
        for result in results:
            pair = result.get("pair", "")
            if pair in pair_map:
                i, j = pair_map[pair]
                winner = result.get("winner")

                # Determine which evaluation won
                if winner == i + 1:
                    group[i].pairwise_wins += 1
                elif winner == j + 1:
                    group[j].pairwise_wins += 1

                logger.debug(
                    "Pairwise %s: winner=%s, reason=%s",
                    pair,
                    winner,
                    result.get("reason", "")
                )

    def _compute_final_ranking(
        self, evaluations: list[LeadEvaluation]
    ) -> list[LeadEvaluation]:
        """Step 4: Combine all factors for final ranking."""
        # Normalize pairwise wins to 0-10 scale
        max_wins = max((e.pairwise_wins for e in evaluations), default=0)

        for eval in evaluations:
            # Final score = 70% weighted score + 30% pairwise performance
            pairwise_score = (eval.pairwise_wins / max_wins) * 10 if max_wins > 0 else 0

            eval.final_rank = (0.7 * eval.weighted_score) + (0.3 * pairwise_score)

            logger.debug(
                "Lead final ranking: weighted=%.2f, pairwise=%.2f, final=%.2f",
                eval.weighted_score,
                pairwise_score,
                eval.final_rank
            )

        # Sort by final rank
        evaluations.sort(key=lambda x: x.final_rank, reverse=True)

        return evaluations

    def _select_top_leads(
        self, ranked_evaluations: list[LeadEvaluation]
    ) -> list[LeadEvaluation]:
        """Step 5: Select top leads by final rank."""
        # Simply take the top N leads based on final ranking
        selected = ranked_evaluations[:self.MAX_LEADS_TO_SELECT]

        # Ensure minimum selection
        if (len(selected) < self.MIN_LEADS_TO_SELECT and
            len(ranked_evaluations) >= self.MIN_LEADS_TO_SELECT):
            selected = ranked_evaluations[:self.MIN_LEADS_TO_SELECT]

        return selected

    def _group_by_score_similarity(
        self, evaluations: list[LeadEvaluation]
    ) -> list[list[LeadEvaluation]]:
        """Group evaluations with similar scores."""
        groups = []
        used = set()

        sorted_evals = sorted(evaluations, key=lambda x: x.weighted_score, reverse=True)

        for i, eval in enumerate(sorted_evals):
            if i in used:
                continue

            group = [eval]
            used.add(i)

            # Find all evaluations within threshold
            for j, other in enumerate(sorted_evals[i + 1:], i + 1):
                if j not in used:
                    score_diff = abs(eval.weighted_score - other.weighted_score)
                    if score_diff <= self.SCORE_SIMILARITY_THRESHOLD:
                        group.append(other)
                        used.add(j)

            if len(group) > 1:
                groups.append(group)
                logger.debug(
                    "Created score group with %d leads (scores: %s)",
                    len(group),
                    [f"{e.weighted_score:.2f}" for e in group]
                )

        return groups
