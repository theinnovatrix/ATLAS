 # Atlas Milestone 8

Milestone 8 adds the first free-first AI brain layer. Atlas still works without
paid services, but it can now use local planning rules first and expose Gemini,
Groq, and other provider slots for later hosted reasoning.

## Implemented now

- Provider settings for free/local Ollama, Gemini free-tier API, Groq
  free/low-cost API, OpenRouter, and OpenAI upgrade path.
- Local deterministic planner that maps flexible natural language to existing
  Atlas tools before any hosted LLM is needed.
- Bilingual English, Hindi, and Urdu preference preserved in provider settings.
- Female voice defaults through Piper and Edge TTS, with ElevenLabs as an
  optional premium upgrade.
- Unknown-command fallback now tries the local AI planner and reports planner
  metadata.

## Try it

```bash
python -m atlas.cli "turn the sound down a bit"
python -m atlas.cli "look up linux voice assistant"
python -m atlas.cli "what is the meaning of atlas"
python -m atlas.cli "start a 15 minute focus session"
python -m atlas.cli "show me my git changes"
```

## Optional keys

```bash
export GEMINI_API_KEY="your_key_here"
export GROQ_API_KEY="your_key_here"
```

Atlas does not require these keys for the local planner. They are upgrade slots
for hosted reasoning in a later milestone.
