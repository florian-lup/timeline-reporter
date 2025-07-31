#!/usr/bin/env python3
"""Debug test for lead discovery with real API calls.

This script tests the lead discovery functionality by making actual API calls
to Perplexity and saving the results locally for debugging purposes.
It follows the exact same flow as the real lead_discovery service.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from clients import PerplexityClient
from config.discovery_config import (
    DISCOVERY_CATEGORIES,
    DISCOVERY_CATEGORY_INSTRUCTIONS,
)
from services.lead_discovery import _json_to_leads
from utils import logger


def main() -> None:
    """Run the debug test for lead discovery."""
    logger.info("🔍 Starting debug test for lead discovery...")

    # Create debug output directory
    debug_dir = Path("debug/output/discovery_output")
    debug_dir.mkdir(exist_ok=True)

    # Initialize Perplexity client
    try:
        perplexity_client = PerplexityClient()
        logger.info("✓ Perplexity client initialized successfully")
    except Exception as exc:
        logger.error("✗ Failed to initialize Perplexity client: %s", exc)
        return

    # Follow the exact same flow as lead_discovery.py
    all_leads = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Debug data collection
    debug_data: dict[str, Any] = {
        "timestamp": timestamp,
        "categories": {},
        "total_leads": 0,
        "files_created": [],
    }

    # Use centralized category configuration - test ONLY first category for debugging
    for category_name in DISCOVERY_CATEGORIES[:1]:
        logger.info("  📰 Scanning %s sources...", category_name)

        try:
            instructions = DISCOVERY_CATEGORY_INSTRUCTIONS[category_name]

            # Get the raw response with <think> content for debugging (structured)
            raw_response_with_thinking = _debug_lead_discovery_with_thinking(
                perplexity_client, instructions
            )

            # Extract just the <think> content for analysis
            thinking_content = _extract_thinking_content(raw_response_with_thinking)

            # Get the clean JSON response (structured output - same as normal flow)
            response_text = perplexity_client.lead_discovery(instructions)
            category_leads = _json_to_leads(response_text)

            # ALSO test unstructured output for comparison
            unstructured_response = _debug_unstructured_discovery(perplexity_client, instructions)
            unstructured_content = str(unstructured_response["choices"][0]["message"]["content"])

            logger.info(
                "  ✓ %s: %d leads found",
                category_name.capitalize(),
                len(category_leads),
            )

            # Log each individual lead with first 5 words for tracking (same as real service)
            for idx, lead in enumerate(category_leads, 1):
                first_words = " ".join(lead.discovered_lead.split()[:5]) + "..."
                logger.info("    📋 Lead %d/%d - %s", idx, len(category_leads), first_words)

            all_leads.extend(category_leads)

            # Save debug files for this category
            raw_file = debug_dir / f"raw_response_{category_name}_{timestamp}.json"
            with Path(raw_file).open("w", encoding="utf-8") as f:
                f.write(response_text)

            leads_data = [
                {
                    "discovered_lead": lead.discovered_lead,
                    "date": lead.date,
                }
                for lead in category_leads
            ]

            leads_file = debug_dir / f"parsed_leads_{category_name}_{timestamp}.json"
            with Path(leads_file).open("w", encoding="utf-8") as f:
                json.dump(leads_data, f, indent=2, ensure_ascii=False)

                # Save unstructured response for comparison
                unstructured_file = (
                    debug_dir / f"unstructured_response_{category_name}_{timestamp}.json"
                )
                with Path(unstructured_file).open("w", encoding="utf-8") as unstructured_f:
                    json.dump(unstructured_response, unstructured_f, indent=2, ensure_ascii=False)
                logger.info("📝 Unstructured response saved to: %s", unstructured_file)

                # Log comparison between structured vs unstructured
                logger.info("📊 Structured JSON length: %d chars", len(response_text))
                logger.info("📊 Unstructured content length: %d chars", len(unstructured_content))

                # Save thinking content if it exists
                thinking_file = None
                if thinking_content:
                    thinking_file = debug_dir / f"thinking_{category_name}_{timestamp}.txt"
                    with Path(thinking_file).open("w", encoding="utf-8") as thinking_f:
                        thinking_f.write(thinking_content)
                    logger.info("🧠 Thinking content saved to: %s", thinking_file)

                    # Log thinking content to console (truncated)
                    max_preview_length = 200
                    thinking_preview = (
                        thinking_content[:max_preview_length] + "..."
                        if len(thinking_content) > max_preview_length
                        else thinking_content
                    )
                    logger.info("🧠 AI Thinking: %s", thinking_preview)

                # Store debug info for this category
                debug_data["categories"][category_name] = {
                    "instructions": instructions,
                    "structured_response_length": len(response_text),
                    "unstructured_response_length": len(unstructured_content),
                    "thinking_length": len(thinking_content) if thinking_content else 0,
                    "leads_count": len(category_leads),
                    "leads_titles": [lead.discovered_lead for lead in category_leads],
                    "raw_file": str(raw_file),
                    "leads_file": str(leads_file),
                    "unstructured_file": str(unstructured_file),
                    "thinking_file": str(thinking_file) if thinking_file else None,
                }
                files_created = [str(raw_file), str(leads_file), str(unstructured_file)]
                if thinking_file:
                    files_created.append(str(thinking_file))
                debug_data["files_created"].extend(files_created)

        except Exception as exc:
            logger.error("  ✗ %s: Discovery failed - %s", category_name.capitalize(), exc)

            # Save error information for this category
            error_file = debug_dir / f"error_{category_name}_{timestamp}.json"
            error_data = {
                "category": category_name,
                "timestamp": timestamp,
                "error": str(exc),
                "error_type": type(exc).__name__,
            }

            with Path(error_file).open("w", encoding="utf-8") as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)

            debug_data["categories"][category_name] = {
                "error": str(exc),
                "error_file": str(error_file),
            }
            debug_data["files_created"].append(str(error_file))

            # Continue with other categories even if one fails (same as real service)
            continue

    # Save overall summary
    debug_data["total_leads"] = len(all_leads)
    summary_file = debug_dir / f"debug_summary_{timestamp}.json"
    with Path(summary_file).open("w", encoding="utf-8") as f:
        json.dump(debug_data, f, indent=2, ensure_ascii=False)
    debug_data["files_created"].append(str(summary_file))

    # Print final results (same format as real service would return)
    logger.info("🎯 Debug test completed")
    logger.info("📊 Total leads discovered: %d", len(all_leads))

    print("\n🎯 DEBUG RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total leads found: {len(all_leads)}")
    print("Categories tested: 1 (debug mode - first category only)")
    print("\n🔄 Testing both STRUCTURED and UNSTRUCTURED outputs:")
    print("  📋 Structured: Uses JSON schema to force consistent format")
    print("  📝 Unstructured: Natural response format from Perplexity")
    print("\nBreakdown by category:")

    for category_name in DISCOVERY_CATEGORIES[:1]:
        if category_name in debug_data["categories"]:
            category_data = debug_data["categories"][category_name]
            if "error" in category_data:
                print(f"  ✗ {category_name}: ERROR - {category_data['error']}")
            else:
                thinking_info = (
                    f" (thinking: {category_data['thinking_length']} chars)"
                    if category_data.get("thinking_length", 0) > 0
                    else ""
                )
                structured_len = category_data.get("structured_response_length", 0)
                unstructured_len = category_data.get("unstructured_response_length", 0)
                print(f"  ✓ {category_name}: {category_data['leads_count']} leads{thinking_info}")
                print(
                    f"    📊 Structured: {structured_len} chars | Unstructured: {unstructured_len} chars"
                )
        else:
            print(f"  ? {category_name}: No data")

    print(f"\nAll debug files saved in: {debug_dir}")
    print(f"Summary file: {summary_file.name}")
    print("\nFile types created:")
    print("  - raw_response_*.json: Clean structured JSON response from Perplexity")
    print("  - unstructured_response_*.json: Natural chat completion response from Perplexity")
    print("  - parsed_leads_*.json: Extracted lead objects from structured response")
    print("  - thinking_*.txt: AI reasoning process (<think> content)")
    print("  - debug_summary_*.json: Overall test summary")
    print("\n💡 Compare structured vs unstructured files to see:")
    print("   • How JSON schema affects response format")
    print("   • Response length differences")
    print("   • Parsing complexity differences")


def _debug_lead_discovery_with_thinking(perplexity_client: PerplexityClient, prompt: str) -> str:
    """Debug version of lead_discovery that returns raw response with <think> content."""
    import httpx

    from config.discovery_config import (
        DISCOVERY_SYSTEM_PROMPT,
        DISCOVERY_TIMEOUT_SECONDS,
        LEAD_DISCOVERY_JSON_SCHEMA,
        LEAD_DISCOVERY_MODEL,
        SEARCH_AFTER_DATE_FILTER as DISCOVERY_SEARCH_AFTER_DATE_FILTER,
        SEARCH_CONTEXT_SIZE as DISCOVERY_SEARCH_CONTEXT_SIZE,
    )

    # Same payload as the real lead_discovery method
    payload = {
        "model": LEAD_DISCOVERY_MODEL,
        "messages": [
            {
                "role": "system",
                "content": DISCOVERY_SYSTEM_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
        "web_search_options": {
            "search_context_size": DISCOVERY_SEARCH_CONTEXT_SIZE,
        },
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": LEAD_DISCOVERY_JSON_SCHEMA},
        },
    }

    # Add precise date filtering
    if DISCOVERY_SEARCH_AFTER_DATE_FILTER:
        payload["search_after_date_filter"] = DISCOVERY_SEARCH_AFTER_DATE_FILTER

    # Make the API call directly to get raw response
    timeout = httpx.Timeout(DISCOVERY_TIMEOUT_SECONDS)
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=perplexity_client._headers,
        )
        response.raise_for_status()
        data = response.json()

    # Return the raw content with <think> tags intact
    return str(data["choices"][0]["message"]["content"])


def _debug_unstructured_discovery(
    perplexity_client: PerplexityClient, prompt: str
) -> dict[str, Any]:
    """Debug version that returns natural unstructured response from Perplexity."""
    import httpx

    from config.discovery_config import (
        DISCOVERY_SYSTEM_PROMPT,
        DISCOVERY_TIMEOUT_SECONDS,
        LEAD_DISCOVERY_MODEL,
        SEARCH_AFTER_DATE_FILTER as DISCOVERY_SEARCH_AFTER_DATE_FILTER,
        SEARCH_CONTEXT_SIZE as DISCOVERY_SEARCH_CONTEXT_SIZE,
    )

    # Same payload as structured version but WITHOUT response_format
    payload = {
        "model": LEAD_DISCOVERY_MODEL,
        "messages": [
            {
                "role": "system",
                "content": DISCOVERY_SYSTEM_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
        "web_search_options": {
            "search_context_size": DISCOVERY_SEARCH_CONTEXT_SIZE,
        },
        # NOTE: NO response_format - this gets natural response
    }

    # Add precise date filtering
    if DISCOVERY_SEARCH_AFTER_DATE_FILTER:
        payload["search_after_date_filter"] = DISCOVERY_SEARCH_AFTER_DATE_FILTER

    # Make the API call directly to get unstructured response
    timeout = httpx.Timeout(DISCOVERY_TIMEOUT_SECONDS)
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=perplexity_client._headers,
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    # Return the full response data (not just content)


def _extract_thinking_content(raw_content: str) -> str:
    """Extract just the <think>...</think> content from the response."""
    import re

    # Find content between <think> and </think> tags
    think_match = re.search(r"<think>(.*?)</think>", raw_content, re.DOTALL)
    if think_match:
        return think_match.group(1).strip()
    return ""


if __name__ == "__main__":
    main()
