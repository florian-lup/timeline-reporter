"""Centralized configuration for lead research system.

This module contains all settings, prompts, and configuration data
related to lead research and story generation.
"""

# ---------------------------------------------------------------------------
# Research Model Configuration
# ---------------------------------------------------------------------------
LEAD_RESEARCH_MODEL: str = "sonar-pro"

# ---------------------------------------------------------------------------
# Research System Prompt
# ---------------------------------------------------------------------------
RESEARCH_SYSTEM_PROMPT = (
    "You are an investigative journalist with expertise in current events "
    "analysis. Focus on accuracy, clarity, and comprehensive coverage. "
    "Provide factual reporting with proper context and balanced perspective."
)

# ---------------------------------------------------------------------------
# Research Instructions Template
# ---------------------------------------------------------------------------
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
# Research Timeouts and Limits
# ---------------------------------------------------------------------------
RESEARCH_TIMEOUT_SECONDS: int = 240
