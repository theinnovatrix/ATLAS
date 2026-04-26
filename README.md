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

## Install and run

Use these commands from the project root.

On Ubuntu, Debian, or Parrot OS, install the Python virtual-environment package
first if `python3 -m venv .venv` fails:

```bash
sudo apt-get update
sudo apt-get install -y python3-venv
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m atlas.cli "system info"
```

You can also install the test/dev tools:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Example commands

```bash
python -m atlas.cli "what can you do"
python -m atlas.cli "system info"
python -m atlas.cli "Delhi ka mausam batao"
python -m atlas.cli "calculate 12 * 8"
python -m atlas.cli "translate hello"
python -m atlas.cli "volume 30"
```

Commands that can change the system require confirmation. For example:

```bash
python -m atlas.cli "volume 30" --confirm
```

Atlas is currently a text-command foundation. Full microphone listening, GUI,
screen recording, and deeper desktop automation are planned follow-up milestones.

## Optional providers

Atlas works without paid keys for the current milestone. Later upgrades can use:

- `GROQ_API_KEY` for low-cost hosted LLM or Whisper.
- `OPENROUTER_API_KEY` for free/low-cost model routing.
- `ELEVENLABS_API_KEY` for premium female TTS voices.
- `SERPAPI_API_KEY` for structured web search.

Set keys only in your shell or a local ignored environment file, never in source
code.

## Development workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
```
