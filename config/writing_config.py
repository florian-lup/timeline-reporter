"""Centralized configuration for story writing system.

This module contains all settings, prompts, and configuration data
related to story writing.
"""

# ---------------------------------------------------------------------------
# Writing Model Configuration
# ---------------------------------------------------------------------------
WRITING_MODEL: str = "gpt-4.1-2025-04-14"

# ---------------------------------------------------------------------------
# Writing System Prompt
# ---------------------------------------------------------------------------
WRITING_SYSTEM_PROMPT = """
You are an award-winning news journalist writing for a global general-interest audience. Your reporting adheres to the core principles of journalism—accuracy, clarity, balance, and integrity.

Write in Associated Press (AP) style: short, active sentences, objective tone, and no first-person narration. Assume the reader is intelligent but busy; prioritize the most newsworthy facts first, then provide context and analysis. When facts are uncertain, clearly attribute or qualify them. Avoid sensationalism, speculation, or editorializing.

Output Requirements:
1. headline – ≤ 10 words, Title Case, no period.
2. summary – 80-100 words, present tense, standalone overview.
3. body – 700-1000 words, AP style, includes:
   • Lead paragraph (25-40 words) summarizing the key news.
   • Subsequent paragraphs expanding on who, what, when, where, why, and how.
   • Relevant background, quotes, and data from the report.
   • Balanced perspectives with clear attribution for claims.
   • Final paragraph that looks ahead or explains implications.
4. tag – single lowercase category (e.g., politics, technology, business, health, etc.).

Think through the structure before writing; then produce the story following the JSON schema exactly.
""".strip()

# ---------------------------------------------------------------------------
# Writing Instructions Template
# ---------------------------------------------------------------------------
WRITING_INSTRUCTIONS = """
Using ONLY the information provided in the lead report below, craft a complete news story.

Report:
{lead_report}
""".strip()

# ---------------------------------------------------------------------------
# JSON Schema for Structured Output
# ---------------------------------------------------------------------------
STORY_WRITING_SCHEMA = {
    "name": "news_story",
    "schema": {
        "type": "object",
        "properties": {
            "headline": {
                "type": "string",
                "description": "News headline, ≤ 15 words, Title Case, no period",
            },
            "summary": {
                "type": "string",
                "description": "80-120 words, present tense, standalone overview",
            },
            "body": {
                "type": "string",
                "description": "1200-2000 words, AP style news article body",
            },
            "tag": {
                "type": "string",
                "description": "Single lowercase category (e.g., politics, technology, business, health)",
            },
        },
        "required": ["headline", "summary", "body", "tag"],
        "additionalProperties": False,
    },
}
