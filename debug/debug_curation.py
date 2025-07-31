#!/usr/bin/env python3
"""Debug test for lead curation using real API calls.

This script tests the lead curation functionality by making actual API calls
to OpenAI and processing the provided sample leads through the complete
curation pipeline, saving detailed results for debugging purposes.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from clients import OpenAIClient
from config.curation_config import (
    CURATION_MODEL,
    MAX_LEADS,
    MIN_SCORE,
    CRITERIA_WEIGHTS,
)
from models import Lead
from services.lead_curation import curate_leads
from utils import logger


def create_sample_leads() -> list[Lead]:
    """Create Lead objects from the provided sample text."""
    sample_texts = [
        "President Trump announced frameworks for new trade agreements with Japan and the Philippines, reducing U.S. tariffs on Japanese imports to 15% and Philippine goods to 19%. The deals include enhanced military cooperation, particularly significant amid China's aggression in the South China Sea, with Philippine President Marcos stating the U.S. remains their 'strongest partner.' This strengthens U.S. economic and strategic positioning in the Indo-Pacific.",
        
        "Trump called for criminal charges against former President Barack Obama and other officials, alleging treason over altered intelligence reports related to Trump-Russia investigations. This follows a criminal referral by Director of National Intelligence Tulsi Gabbard, who cited a '180-degree shift' in intelligence assessments during the 2016–2017 transition period, escalating political tensions in Washington.",
        
        "Humanitarian catastrophe deepens in Gaza as UN Secretary-General António Guterres warns of 'starvation knocking on every door.' Cease-fire negotiations are deadlocked over food aid distribution, with EU foreign policy chief Kaja Kallas threatening 'all options remain on the table' if Israel fails to improve access. U.S. envoy Steve Witkoff is mediating talks in Rome and Qatar to finalize a hostage deal.",
        
        "Turkey vowed direct intervention to prevent Syria's fragmentation after clashes in the south, with Foreign Minister Hakan Fidan pledging to block militant autonomy. This aligns with Turkey's increasing regional assertiveness, as President Erdoğan praised the nation's defense industry growth at the IDEF expo, where localization surpassed 80%.",
        
        "Ukraine saw its largest wartime protests targeting President Zelensky after he signed legislation weakening anti-corruption agencies. Protesters condemned what they called concessions to 'Russian influence,' while Zelensky defended the move as necessary for sovereignty. Meanwhile, Ukraine's military commander urgently requested more U.S. and European air defenses against intensified Russian strikes.",
        
        "The U.S. imposed sanctions on a Houthi-linked petroleum smuggling network spanning Yemen and the UAE, targeting Iran-backed militant activities. This coincides with fresh sanctions against the Houthis as part of broader efforts to disrupt Iran's regional influence and curtail its destabilizing proxy warfare in the Middle East.",
        
        "China rebuked the U.S. for withdrawing from UNESCO—its third exit—calling it 'not what a major country should do.' This occurred amid U.S.-China trade talks scheduled in Stockholm, where Treasury Secretary Scott Bessent will discuss extending tariff truces and China's oil purchases from Russia/Iran. Trump also teased a 'not too distant' visit to China.",
        
        "Portugal endorsed Morocco's Western Sahara autonomy plan, with Foreign Minister Paulo Rangel calling it a 'serious and credible basis.' This aligns with growing Western support for Morocco's proposal, contrasting Spain's previous stance and shifting diplomatic dynamics in North Africa amid regional instability.",
        
        "The International Court of Justice will issue a landmark advisory opinion on state obligations to combat climate change and legal consequences for emissions-causing harm. While non-binding, the ruling is expected to influence global climate litigation and pressure nations to strengthen environmental policies under international law.",
        
        "A Syrian American was executed during sectarian violence in Sweida, Syria, highlighting escalating tensions. The killing follows anti-government protests in the Druze-majority region, underscoring Syria's persistent instability and the risks facing diaspora returnees amid the country's protracted conflict.",
        
        "Students protested in Bangladesh demanding transparency after an air force jet crashed into a school, killing 19. Demonstrators called for accountability and investigations into military safety protocols, reflecting public anger over governance failures as the death toll continues to rise.",
    ]
    
    return [Lead(discovered_lead=text) for text in sample_texts]


def save_test_outputs(
    original_leads: list[Lead], 
    curated_leads: list[Lead], 
    test_start_time: datetime,
    raw_response: str | None = None,
    debug_info: dict[str, object] | None = None,
    scoring_results: list[dict[str, object]] | None = None
) -> None:
    """Save comprehensive test results to debug/output/curation_output directory."""
    output_dir = Path("debug/output/curation_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = test_start_time.strftime("%Y%m%d_%H%M%S")
    
    # Save original leads
    original_leads_file = output_dir / f"curation_original_leads_{timestamp}.json"
    with open(original_leads_file, "w", encoding="utf-8") as f:
        original_data = {
            "timestamp": test_start_time.isoformat(),
            "total_leads": len(original_leads),
            "leads": [
                {
                    "index": i + 1,
                    "discovered_lead": lead.discovered_lead,
                    "date": lead.date,
                    "sources": lead.sources,
                    "report": lead.report,
                }
                for i, lead in enumerate(original_leads)
            ]
        }
        json.dump(original_data, f, indent=2, ensure_ascii=False)
    
    # Save curated leads after evaluation
    curated_leads_file = output_dir / f"curation_selected_leads_{timestamp}.json"
    with open(curated_leads_file, "w", encoding="utf-8") as f:
        curated_data = {
            "timestamp": test_start_time.isoformat(),
            "original_count": len(original_leads),
            "curated_count": len(curated_leads),
            "filtered_out": len(original_leads) - len(curated_leads),
            "curation_config": {
                "model": CURATION_MODEL,
                "max_leads": MAX_LEADS,
                "min_score": MIN_SCORE,
                "criteria_weights": CRITERIA_WEIGHTS,
            },
            "curated_leads": [
                {
                    "index": i + 1,
                    "discovered_lead": lead.discovered_lead,
                    "date": lead.date,
                    "sources": lead.sources,
                    "report": lead.report,
                }
                for i, lead in enumerate(curated_leads)
            ]
        }
        json.dump(curated_data, f, indent=2, ensure_ascii=False)
    
    # Save raw OpenAI response if available
    if raw_response:
        raw_response_file = output_dir / f"curation_raw_response_{timestamp}.json"
        with open(raw_response_file, "w", encoding="utf-8") as f:
            f.write(raw_response)
    
    # Save comprehensive summary
    summary_file = output_dir / f"curation_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        selection_rate = round(len(curated_leads) / len(original_leads) * 100, 2) if original_leads else 0
        
        summary_data = {
            "test_metadata": {
                "timestamp": test_start_time.isoformat(),
                "test_type": "curation_debug",
                "description": "Real API test of lead curation pipeline with multi-criteria evaluation",
                "model_used": CURATION_MODEL,
            },
            "curation_config": {
                "model": CURATION_MODEL,
                "max_leads": MAX_LEADS,
                "min_score": MIN_SCORE,
                "criteria_weights": CRITERIA_WEIGHTS,
            },
            "results": {
                "total_input_leads": len(original_leads),
                "curated_output_leads": len(curated_leads),
                "leads_filtered_out": len(original_leads) - len(curated_leads),
                "selection_rate_percent": selection_rate,
            },
            "debug_info": debug_info or {},
            "detailed_scoring": scoring_results or [],
            "file_outputs": {
                "original_leads": str(original_leads_file.name),
                "curated_leads": str(curated_leads_file.name),
                "raw_response": str(raw_response_file.name) if raw_response else None,
                "summary": str(summary_file.name),
            },
            "lead_analysis": {
                "selected_lead_previews": [
                    " ".join(lead.discovered_lead.split()[:8]) + "..."
                    for lead in curated_leads
                ],
                "filtered_lead_previews": [
                    " ".join(lead.discovered_lead.split()[:8]) + "..."
                    for lead in original_leads
                    if lead not in curated_leads
                ]
            }
        }
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    logger.info("💾 Saved test outputs:")
    logger.info("  📄 Original leads: %s", original_leads_file.name)
    logger.info("  📄 Curated leads: %s", curated_leads_file.name)
    if raw_response:
        logger.info("  📄 Raw response: %s", raw_response_file.name)
    logger.info("  📄 Summary: %s", summary_file.name)


def capture_raw_openai_response(openai_client: OpenAIClient, leads: list[Lead]) -> str:
    """Capture the raw OpenAI response for debugging purposes."""
    from config.curation_config import (
        CRITERIA_EVALUATION_PROMPT_TEMPLATE,
        CRITERIA_EVALUATION_SCHEMA,
        CRITERIA_EVALUATION_SYSTEM_PROMPT,
    )
    
    # Format leads exactly as the real service does
    leads_text = "\n".join(f"{i + 1}. {lead.discovered_lead}" for i, lead in enumerate(leads))
    user_prompt = CRITERIA_EVALUATION_PROMPT_TEMPLATE.format(leads_text=leads_text)
    
    # Make the same API call as the real service
    logger.info("🤖 Making OpenAI API call for criteria evaluation...")
    raw_response = openai_client.chat_completion(
        user_prompt, 
        model=CURATION_MODEL, 
        response_format={
            "type": "json_schema",
            "json_schema": CRITERIA_EVALUATION_SCHEMA
        },
        system_prompt=CRITERIA_EVALUATION_SYSTEM_PROMPT
    )
    
    logger.info("✅ Raw OpenAI response captured (%d characters)", len(raw_response))
    return raw_response


def parse_and_display_scores(raw_response: str, leads: list[Lead]) -> list[dict[str, object]]:
    """Parse the raw OpenAI response and display detailed scoring for each lead."""
    import json
    
    logger.info("🔍 DETAILED SCORING ANALYSIS:")
    logger.info("=" * 80)
    
    try:
        scores_data = json.loads(raw_response)
        evaluations_data = scores_data["evaluations"]
        
        detailed_results = []
        
        for i, lead in enumerate(leads):
            # Find scores for this lead
            lead_scores = next(
                score_entry for score_entry in evaluations_data 
                if score_entry["index"] == i + 1
            )
            
            # Calculate weighted score
            criteria_scores = {
                k: float(lead_scores[k]) for k in CRITERIA_WEIGHTS
            }
            weighted_score = sum(score * CRITERIA_WEIGHTS[criterion] for criterion, score in criteria_scores.items())
            weighted_score = round(weighted_score, 2)
            
            # Create result entry
            result = {
                "index": i + 1,
                "lead_preview": " ".join(lead.discovered_lead.split()[:8]) + "...",
                "criteria_scores": criteria_scores,
                "weighted_score": weighted_score,
                "passed_threshold": weighted_score >= MIN_SCORE,
                "reasoning": lead_scores["brief_reasoning"]
            }
            detailed_results.append(result)
            
            # Display detailed scoring
            status = "✅ SELECTED" if weighted_score >= MIN_SCORE else "❌ FILTERED"
            logger.info(f"📊 Lead {i+1:2d}/11: {status} (Score: {weighted_score:.2f})")
            logger.info(f"   Topic: {result['lead_preview']}")
            logger.info(f"   Scores: Impact={criteria_scores['impact']} Proximity={criteria_scores['proximity']} "
                       f"Prominence={criteria_scores['prominence']} Relevance={criteria_scores['relevance']}")
            logger.info(f"           Hook={criteria_scores['hook']} Novelty={criteria_scores['novelty']} "
                       f"Conflict={criteria_scores['conflict']}")
            logger.info(f"   Reasoning: {lead_scores['brief_reasoning']}")
            logger.info("")
        
        # Summary statistics
        selected_count = sum(1 for r in detailed_results if r["passed_threshold"])
        avg_score = sum(r["weighted_score"] for r in detailed_results) / len(detailed_results)
        
        logger.info("📈 SCORING SUMMARY:")
        logger.info(f"   Average score: {avg_score:.2f}")
        logger.info(f"   Threshold: {MIN_SCORE:.2f}")
        logger.info(f"   Above threshold: {selected_count}/{len(detailed_results)} leads")
        logger.info(f"   Score range: {min(r['weighted_score'] for r in detailed_results):.2f} - {max(r['weighted_score'] for r in detailed_results):.2f}")
        
        return detailed_results
        
    except Exception as e:
        logger.error(f"❌ Failed to parse scoring data: {e}")
        return []


def apply_curation_logic(raw_response: str, leads: list[Lead]) -> list[Lead]:
    """Apply the exact same curation logic as lead_curation.py to the captured response."""
    import json
    from models import LeadEvaluation
    
    logger.info("🔄 Applying curation logic (exactly like lead_curation.py)...")
    
    # Step 1: Parse response - same as lead_curation.py
    scores_data = json.loads(raw_response)
    evaluations_data = scores_data["evaluations"]
    
    evaluations = []
    for i, lead in enumerate(leads):
        # Find scores for this lead - same logic as lead_curation.py
        lead_scores = next(
            score_entry for score_entry in evaluations_data 
            if score_entry["index"] == i + 1
        )
        
        criteria_scores = {
            k: float(lead_scores[k]) for k in CRITERIA_WEIGHTS
        }
        
        # Calculate weighted score - same formula as lead_curation.py
        weighted = sum(score * CRITERIA_WEIGHTS[criterion] for criterion, score in criteria_scores.items())
        weighted = round(weighted, 2)
        
        evaluations.append(
            LeadEvaluation(
                lead=lead,
                criteria_scores=criteria_scores,
                weighted_score=weighted,
            )
        )
        
        first_words = " ".join(lead.discovered_lead.split()[:5]) + "..."
        reasoning = lead_scores["brief_reasoning"]
        reasoning_display = reasoning[:80] + ("..." if len(reasoning) > 80 else "")
        logger.info(
            "  📊 Lead %d/%d scored %.1f - %s: %s",
            i + 1,
            len(leads),
            weighted,
            first_words,
            reasoning_display,
        )
    
    # Step 2: Filter by minimum threshold - same as lead_curation.py
    qualified = [e for e in evaluations if e.weighted_score >= MIN_SCORE]
    failed_threshold = [e for e in evaluations if e.weighted_score < MIN_SCORE]
    
    logger.info(
        "  📊 Threshold analysis: %d/%d leads passed minimum score requirement (%.1f)",
        len(qualified),
        len(leads),
        MIN_SCORE,
    )
    
    if failed_threshold:
        logger.info(
            "  📉 %d leads below threshold: scores %.1f-%.1f",
            len(failed_threshold),
            min(e.weighted_score for e in failed_threshold),
            max(e.weighted_score for e in failed_threshold),
        )
    
    if not qualified:
        logger.warning(
            "No leads passed minimum threshold (%.2f), returning empty list",
            MIN_SCORE,
        )
        return []
    
    # Step 3: Final ranking - same as lead_curation.py
    for eval in qualified:
        eval.final_rank = eval.weighted_score
    
    qualified.sort(key=lambda x: x.final_rank, reverse=True)
    
    # Step 4: Select top leads - same as lead_curation.py
    selected = qualified[:MAX_LEADS]
    
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


def analyze_curation_results(original_leads: list[Lead], curated_leads: list[Lead]) -> dict[str, object]:
    """Analyze the curation results and return debug information."""
    analysis = {
        "lead_count_analysis": {
            "input_count": len(original_leads),
            "output_count": len(curated_leads),
            "filtered_count": len(original_leads) - len(curated_leads),
            "selection_rate": round(len(curated_leads) / len(original_leads) * 100, 2) if original_leads else 0,
        },
        "content_analysis": {
            "avg_lead_length_chars": sum(len(lead.discovered_lead) for lead in original_leads) // len(original_leads) if original_leads else 0,
            "avg_selected_length_chars": sum(len(lead.discovered_lead) for lead in curated_leads) // len(curated_leads) if curated_leads else 0,
        },
        "selection_patterns": {
            "selected_lead_topics": [
                " ".join(lead.discovered_lead.split()[:5]) + "..."
                for lead in curated_leads
            ],
            "filtered_lead_topics": [
                " ".join(lead.discovered_lead.split()[:5]) + "..."
                for lead in original_leads
                if lead not in curated_leads
            ]
        }
    }
    
    return analysis


def main() -> None:
    """Run the curation debug test with real API calls."""
    test_start_time = datetime.now()
    logger.info("🧪 LEAD CURATION DEBUG TEST STARTED")
    logger.info("⏰ Test started at: %s", test_start_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # Check for required environment variables
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("❌ Missing required environment variable: OPENAI_API_KEY")
            return
        
        # Initialize real OpenAI client
        logger.info("📡 Initializing OpenAI client...")
        openai_client = OpenAIClient()
        logger.info("✅ OpenAI client initialized successfully")
        
        # Log curation configuration
        logger.info("⚙️ Curation Configuration:")
        logger.info("  Model: %s", CURATION_MODEL)
        logger.info("  Max leads: %d", MAX_LEADS)
        logger.info("  Min score threshold: %.2f", MIN_SCORE)
        logger.info("  Criteria weights: %s", CRITERIA_WEIGHTS)
        
        # Create sample leads
        logger.info("📝 Creating sample leads from provided texts...")
        original_leads = create_sample_leads()
        logger.info("✅ Created %d sample leads for evaluation", len(original_leads))
        
        # Log sample lead previews
        logger.info("📋 Sample leads preview:")
        for i, lead in enumerate(original_leads, 1):
            preview = " ".join(lead.discovered_lead.split()[:8]) + "..."
            logger.info("  %d. %s", i, preview)
        
        # Run curation with single OpenAI call (exactly like the real service)
        logger.info("🔄 Starting lead curation pipeline with single OpenAI call...")
        raw_response = capture_raw_openai_response(openai_client, original_leads)
        
        # Parse and display detailed scoring from the same response
        scoring_results = parse_and_display_scores(raw_response, original_leads)
        
        # Apply the same curation logic as lead_curation.py to the same response
        curated_leads = apply_curation_logic(raw_response, original_leads)
        
        # Analyze results
        analysis = analyze_curation_results(original_leads, curated_leads)
        
        # Log results
        logger.info("✅ CURATION COMPLETE:")
        logger.info("  📊 Original leads: %d", len(original_leads))
        logger.info("  📊 Curated leads: %d", len(curated_leads))
        logger.info("  📊 Leads filtered out: %d", len(original_leads) - len(curated_leads))
        if isinstance(analysis, dict) and "lead_count_analysis" in analysis:
            logger.info("  📊 Selection rate: %.1f%%", analysis["lead_count_analysis"]["selection_rate"])  # type: ignore[index]
        
        if curated_leads:
            logger.info("🏆 Selected leads:")
            for i, lead in enumerate(curated_leads, 1):
                preview = " ".join(lead.discovered_lead.split()[:8]) + "..."
                logger.info("  %d. %s", i, preview)
        else:
            logger.warning("⚠️ No leads passed the curation criteria!")
        
        # Save comprehensive outputs
        logger.info("💾 Saving test outputs to debug/output...")
        save_test_outputs(original_leads, curated_leads, test_start_time, raw_response, analysis, scoring_results)
        
        # Final summary
        test_duration = datetime.now() - test_start_time
        logger.info("🎉 TEST COMPLETED SUCCESSFULLY")
        logger.info("⏱️ Test duration: %s", str(test_duration).split('.')[0])
        
        # Print detailed console summary
        print(f"\n🎯 CURATION DEBUG RESULTS SUMMARY")
        print(f"=" * 60)
        print(f"Test completed: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {str(test_duration).split('.')[0]}")
        print(f"Model used: {CURATION_MODEL}")
        print(f"\n📊 RESULTS:")
        print(f"  Input leads: {len(original_leads)}")
        print(f"  Selected leads: {len(curated_leads)}")
        print(f"  Filtered out: {len(original_leads) - len(curated_leads)}")
        if isinstance(analysis, dict) and "lead_count_analysis" in analysis:
            print(f"  Selection rate: {analysis['lead_count_analysis']['selection_rate']:.1f}%")  # type: ignore[index]
        
        print(f"\n⚙️ CURATION SETTINGS:")
        print(f"  Max leads limit: {MAX_LEADS}")
        print(f"  Min score threshold: {MIN_SCORE}")
        print(f"  Criteria weights: {CRITERIA_WEIGHTS}")
        
        if curated_leads:
            print(f"\n🏆 SELECTED LEADS:")
            for i, lead in enumerate(curated_leads, 1):
                preview = " ".join(lead.discovered_lead.split()[:10]) + "..."
                print(f"  {i:2d}. {preview}")
        
        if len(curated_leads) < len(original_leads):
            filtered_leads = [lead for lead in original_leads if lead not in curated_leads]
            print(f"\n❌ FILTERED OUT LEADS:")
            for i, lead in enumerate(filtered_leads, 1):
                preview = " ".join(lead.discovered_lead.split()[:10]) + "..."
                print(f"  {i:2d}. {preview}")
        
        print(f"\n📁 All debug files saved in: debug/output/curation_output/")
        print(f"💡 Files include: original leads, curated leads, raw AI response, and detailed analysis")
        
        # return True  # Removed - function should not return value
        
    except Exception as e:
        logger.error("❌ TEST FAILED: %s", str(e))
        logger.error("📍 Error occurred during curation test execution")
        test_duration = datetime.now() - test_start_time
        print(f"\n❌ CURATION DEBUG TEST FAILED")
        print(f"Error: {str(e)}")
        print(f"Duration before failure: {str(test_duration).split('.')[0]}")
        raise


if __name__ == "__main__":
    main()
