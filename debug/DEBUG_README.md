# Debug Scripts

This directory contains standalone debug scripts for testing various functionality with real API calls and services.

## Files

- `debug_audio.py` - Standalone script for real audio generation testing

## Usage

Run debug scripts from the project root:

```bash
python debug/debug_audio.py
```

## Requirements

Debug scripts require the following environment variables:

- `OPENAI_API_KEY`
- `MONGODB_URI`
- `MONGODB_DATABASE_NAME`
- `MONGODB_COLLECTION_NAME_AUDIO`

## Audio Generation Debug Script

The `debug_audio.py` script:

1. Creates test story objects with sample news content
2. Uses real OpenAI client for script generation and TTS
3. Uses real MongoDB client for persistence
4. Generates actual audio output
5. Saves outputs to `debug/test_output/` directory:
   - Script text file
   - MP3 audio file
   - JSON object (same structure as MongoDB)

## Organization

This debug directory is separate from the main pytest test suite and contains scripts that can be run independently for debugging and manual testing purposes.

All test outputs are contained within the debug directory structure.
