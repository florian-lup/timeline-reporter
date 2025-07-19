"""Centralized configuration for story writing system.

This module contains all settings, prompts, and configuration data
related to story writing using GPT-4o.
"""

# ---------------------------------------------------------------------------
# Writing Model Configuration
# ---------------------------------------------------------------------------
WRITING_MODEL: str = "gpt-4o"
WRITING_TEMPERATURE: float = 0.7

# ---------------------------------------------------------------------------
# Writing System Prompt
# ---------------------------------------------------------------------------
WRITING_SYSTEM_PROMPT = (
    "You are a professional journalist with expertise in writing clear, engaging, "
    "and well-structured news stories. Your writing is concise yet comprehensive, "
    "factual yet engaging, and always maintains journalistic integrity. You write "
    "for a general news audience, explaining complex topics in accessible language "
    "while maintaining accuracy and depth."
)

# ---------------------------------------------------------------------------
# Writing Instructions Template
# ---------------------------------------------------------------------------
WRITING_INSTRUCTIONS = (
    "Based on the following researched context, write a comprehensive news story. "
    "The context contains all the background information, facts, and details you need "
    "to create an accurate, well-structured article.\n\n"
    "Date: {lead_date}\n"
    "Context: {lead_context}\n\n"
    "Write a complete news story with:\n"
    "1. A compelling headline (max 20 words) that captures the essence of the story\n"
    "2. A concise summary (80-120 words) highlighting the key points and "
    "why this matters\n"
    "3. A detailed story body (400-600 words) that:\n"
    "   - Opens with a strong lead paragraph\n"
    "   - Provides comprehensive coverage using the researched context\n"
    "   - Explains the significance and implications\n"
    "   - Maintains objectivity and balanced perspective\n"
    "   - Concludes with forward-looking context or next steps\n"
    "4. An appropriate category tag that best describes the story's "
    "primary subject matter\n\n"
    "Ensure the story reflects the timeliness of the {lead_date} date."
)

# ---------------------------------------------------------------------------
# JSON Format Instructions
# ---------------------------------------------------------------------------
JSON_FORMAT_INSTRUCTION = (
    "\n\nProvide your response as a JSON object with these exact fields:\n"
    "- headline: A compelling headline (max 20 words)\n"
    "- summary: A concise summary (80-120 words)\n"
    "- body: The detailed story body (400-600 words)\n"
    "- tag: A single category tag that best describes the story. Examples include: "
    "politics, economics, technology, health, environment, business, sports, "
    "entertainment, science, crime, education, international, social, or other"
)
