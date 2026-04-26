# Atlas

Atlas is a local-first Linux desktop voice assistant foundation. It starts with a
safe command router, bilingual English and Hindi/Urdu intent handling, free or
offline default providers, and upgrade hooks for paid AI and voice services.

## Current milestone

- Text command CLI: `python -m atlas.cli "system info"`
- Capability registry for the requested system, desktop, productivity, coding,
  web, and media feature set.
- Safety policy for destructive or privileged operations.
- Free-first providers by default: local rules for intent parsing, `pyttsx3` or
  Piper for TTS, Faster-Whisper for offline speech-to-text, and optional Groq,
  OpenAI, ElevenLabs, Azure, or Google provider slots for later upgrades.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
