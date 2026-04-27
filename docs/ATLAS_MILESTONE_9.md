 # Atlas Milestone 9

Milestone 9 adds hosted AI reasoning behind the local planner. Atlas still uses
free/local deterministic planning first, then Gemini or Groq only when a command
is not understood locally.

## Implemented now

- Gemini planner client using `GEMINI_API_KEY`.
- Groq planner client using `GROQ_API_KEY`.
- Strict JSON extraction and schema validation.
- Intent allowlist validation so hosted models cannot invent unsafe tools.
- Hosted planning fallback after local planning and before unknown-command output.
- Mocked tests for provider order, valid plans, invalid JSON, and unsafe intents.

## Expected hosted JSON shape

```json
{"intent": "web_search", "confidence": 0.7, "args": {"target": "linux"}}
```

Atlas accepts only registered, non-dangerous intents. Risky intents still go
through the existing confirmation layer.

## Try it

```bash
export GEMINI_API_KEY="your_key_here"
export GROQ_API_KEY="your_key_here"
python -m atlas.cli "can you look up linux voice assistant for me" --json
python -m atlas.cli "do something Atlas cannot parse locally" --json
```

## Safety boundary

Hosted providers only plan existing Atlas capabilities. They do not execute shell
commands directly and cannot bypass login pages, private APIs, or confirmation
requirements.
