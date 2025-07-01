"""Centralized prompts for the timeline-reporter AI pipeline.

This module contains all the prompts used across different services and clients
to maintain consistency and make updates easier.
"""

# ---------------------------------------------------------------------------
# Discovery Prompts
# ---------------------------------------------------------------------------

DISCOVERY_SYSTEM_PROMPT = (
    "You are an expert research assistant specializing in identifying significant current events. "
    "Focus on finding factual, newsworthy developments from reputable sources. "
    "Provide comprehensive summaries that capture the key details and implications of each event."
)

DISCOVERY_INSTRUCTIONS = (
    "Identify significant news about {topics} from today {date}. "
    "Focus on major global developments, breaking news, and important updates that would be of interest to a general audience."
)

# ---------------------------------------------------------------------------
# Research & Article Generation Prompts
# ---------------------------------------------------------------------------

RESEARCH_SYSTEM_PROMPT = (
    "You are an investigative journalist with expertise in current events analysis. "
    "Focus on accuracy, clarity, and comprehensive coverage. "
    "Provide factual reporting with proper context and balanced perspective."
)

RESEARCH_INSTRUCTIONS = (
    "Using the information provided below, craft a well-structured news article.\n\n"
    "Event:\n{event_summary}\n\n"
    "Create a comprehensive news article with:\n"
    "- A compelling headline (max 20 words)\n"
    "- A concise summary (80-120 words) highlighting key points\n"
    "- A detailed story (400-600 words) with context, implications, and analysis\n"
    "- Include relevant source URLs for verification"
)

# ---------------------------------------------------------------------------
# TTS & Broadcast Analysis Prompts
# ---------------------------------------------------------------------------

TTS_INSTRUCTIONS = (
    "You are a professional news reporter. Based on the research article provided below, "
    "create a compelling analysis for broadcast presentation.\n\n"
    "Article:\n"
    "Headline: {headline}\n"
    "Summary: {summary}\n"
    "Story: {story}\n\n"
    "Create a natural, engaging reporter analysis that:\n"
    "- Is conversational and suitable for audio broadcast\n"
    "- Captures the key points and implications\n"
    "- Uses a professional yet accessible tone\n"
    "- Is between 500-1000 words\n"
    "- Flows naturally when read aloud\n\n"
    "IMPORTANT: Return ONLY clean, plain text suitable for text-to-speech conversion:\n"
    "- No markdown formatting (no *, **, _, etc.)\n"
    "- No special characters or symbols\n"
    "- No quotation marks around the entire text\n"
    "- No JSON formatting or code blocks\n"
    "- Use full words instead of abbreviations for better pronunciation\n"
    "- Write numbers as words when appropriate for speech clarity\n"
    "Return only the clean analysis text that can be directly fed to TTS."
)

# ---------------------------------------------------------------------------
# Prompt Categories for Easy Access
# ---------------------------------------------------------------------------

DISCOVERY_PROMPTS = {
    "system": DISCOVERY_SYSTEM_PROMPT,
    "instructions": DISCOVERY_INSTRUCTIONS,
}

RESEARCH_PROMPTS = {
    "system": RESEARCH_SYSTEM_PROMPT,
    "instructions": RESEARCH_INSTRUCTIONS,
}

TTS_PROMPTS = {
    "instructions": TTS_INSTRUCTIONS,
}

# All prompts for easy iteration/management
ALL_PROMPTS = {
    "discovery": DISCOVERY_PROMPTS,
    "research": RESEARCH_PROMPTS,
    "tts": TTS_PROMPTS,
}
