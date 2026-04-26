# Atlas Milestone 1

Atlas is the renamed assistant foundation. This milestone implements a safe text-command engine,
not the full voice GUI release.

## Implemented now

- Local CLI entry point: `python -m atlas.cli "system info"`.
- English plus Latin-script Hindi/Urdu command parsing for common commands.
- Capability registry for the requested system, desktop, productivity, developer, and web/media
  feature set.
- Safety policy that blocks dangerous actions and requires `CONFIRM_ATLAS_ACTION` for privileged
  operations.
- Free-first provider configuration:
  - LLM: Ollama first, Groq/OpenRouter low-cost upgrade slots, OpenAI paid slot.
  - STT: Faster-Whisper local first, Groq Whisper upgrade slot.
  - TTS: Piper local and Edge TTS free first, ElevenLabs upgrade slot for premium female voices.
  - Search: DuckDuckGo URL fallback first, SerpAPI upgrade slot.

## Voice direction

The requested YouTube voice should be treated as a reference target. Atlas now exposes provider
slots for free female bilingual voices through Edge TTS and paid natural voices through ElevenLabs.
The app should not clone or reuse a third-party voice unless the user has the rights to do that.

## Safety boundary

Atlas can be powerful, but it must not bypass authentication, access private website backends, ignore
platform rules, or silently execute destructive commands. Social platforms should use official APIs,
OAuth, public data, or user-authorized exports.
