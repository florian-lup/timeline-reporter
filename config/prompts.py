"""Centralized prompts for the timeline-reporter AI pipeline.

This module contains all the prompts used across different services and clients
to maintain consistency and make updates easier.
"""

from utils import get_today_formatted

# ---------------------------------------------------------------------------
# Discovery Prompts
# ---------------------------------------------------------------------------

DISCOVERY_SYSTEM_PROMPT = (
    "You are an expert research assistant specializing in identifying "
    "significant current events. Focus on finding factual, newsworthy "
    "developments from reputable sources. Provide comprehensive summaries "
    "that capture the key details and implications of each lead."
    "\n\nStructure your response as a JSON array where each "
    "lead has a 'tip' field containing a comprehensive paragraph "
    "summarizing the lead's significance and key details. Format: "
    '[{"tip": "Comprehensive paragraph describing the lead, its '
    'significance, and key details..."}]'
)

# Category-specific discovery instructions
DISCOVERY_POLITICS_INSTRUCTIONS = (
    f"Identify significant news about politics, geopolitics, and governments "
    f"from today {get_today_formatted()}. Focus on major political developments, "
    "international relations, policy changes, elections, diplomatic events, "
    "and governmental decisions that would be of interest to a global audience. "
    "Return your findings as a JSON array of leads, where each "
    "lead has a 'tip' field containing a comprehensive paragraph "
    "explaining the lead with all key details and implications. Example format: "
    '[{"tip": "Comprehensive paragraph describing the political lead, its '
    'significance, and key details..."}]'
)

DISCOVERY_ENVIRONMENT_INSTRUCTIONS = (
    f"Identify significant news about environment, climate, and natural disasters "
    f"from today {get_today_formatted()}. Focus on climate change developments, "
    "environmental policies, natural disasters, conservation efforts, "
    "extreme weather events, and ecological breakthroughs that would be of "
    "interest to a global audience. Return your findings as a JSON array of leads, "
    "where each lead has a 'tip' field containing a comprehensive paragraph "
    "explaining the lead with all key details and implications. Example format: "
    '[{"tip": "Comprehensive paragraph describing the environmental lead, its '
    'significance, and key details..."}]'
)

DISCOVERY_ENTERTAINMENT_INSTRUCTIONS = (
    f"Identify significant news about celebrities, entertainment, and sports "
    f"from today {get_today_formatted()}. Focus on major celebrity news, "
    "entertainment industry developments, film and music releases, major sporting "
    "achievements, championship events, and cultural phenomena that would be of "
    "interest to a global audience. Return your findings as a JSON array of leads, "
    "where each lead has a 'tip' field containing a comprehensive paragraph "
    "explaining the lead with all key details and implications. Example format: "
    '[{"tip": "Comprehensive paragraph describing the entertainment/sports lead, its '
    'significance, and key details..."}]'
)





# ---------------------------------------------------------------------------
# Research & Story Generation Prompts
# ---------------------------------------------------------------------------

RESEARCH_SYSTEM_PROMPT = (
    "You are an investigative journalist with expertise in current events "
    "analysis. Focus on accuracy, clarity, and comprehensive coverage. "
    "Provide factual reporting with proper context and balanced perspective."
)

RESEARCH_INSTRUCTIONS = (
    "You are a professional journalist tasked with researching and writing a "
    "comprehensive news story based on a lead. Research the lead thoroughly "
    "and write an in-depth, well-sourced story. Focus on accuracy, context, "
    "and providing a complete picture of the situation. Write the story in a "
    "clear, engaging style suitable for a general news audience. Include all "
    "relevant background information and explain the significance of the "
    "story.\n\nLead:\n{lead_summary}\nDate: {lead_date}\n\n"
    "Create a comprehensive news story with:\n"
    "- A compelling headline (max 20 words)\n"
    "- A concise summary (80-120 words) highlighting key points\n"
    "- A detailed story (400-600 words) with context, implications, and "
    "analysis\n- Include relevant source URLs for verification\n"
    "- Ensure the reporting reflects the timeliness and relevance of the "
    "{lead_date} date"
)

# ---------------------------------------------------------------------------
# Prompt Categories for Easy Access
# ---------------------------------------------------------------------------

DISCOVERY_PROMPTS = {
    "system": DISCOVERY_SYSTEM_PROMPT,
    "politics": DISCOVERY_POLITICS_INSTRUCTIONS,
    "environment": DISCOVERY_ENVIRONMENT_INSTRUCTIONS,
    "entertainment": DISCOVERY_ENTERTAINMENT_INSTRUCTIONS,
}

RESEARCH_PROMPTS = {
    "system": RESEARCH_SYSTEM_PROMPT,
    "instructions": RESEARCH_INSTRUCTIONS,
}

# All prompts for easy iteration/management
ALL_PROMPTS = {
    "discovery": DISCOVERY_PROMPTS,
    "research": RESEARCH_PROMPTS,
}
