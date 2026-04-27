# Atlas Milestone 6

Milestone 6 adds local productivity and coding helpers. These features stay
local-first and avoid destructive file or shell actions by default.

## Implemented now

- File helpers for quick search, folder creation, folder size, copy-path
  normalization, zip, unzip, and safe delete planning.
- Notes and todos with optional JSON persistence for tests and future app state.
- Timer, Pomodoro, and local dictionary/calculator utilities.
- Coding helpers for git status, git diff summaries, safe shell command
  suggestions, JSON validation, doc previews, and test-name suggestions.
- CLI routes:
  - `python -m atlas.cli "copy path README.md"`
  - `python -m atlas.cli "zip README.md"`
  - `python -m atlas.cli "git status"`
  - `python -m atlas.cli "git diff"`
  - `python -m atlas.cli "suggest command list files"`
  - `python -m atlas.cli "validate json {\"ok\": true}"`

## Safety boundary

Atlas does not run arbitrary shell commands. It suggests safe commands and only
runs a tiny read-only allowlist.

## Next work

- Persist todos/notes through the future GUI settings layer.
- Add richer file-operation confirmation flows.
- Expand coding helpers with project-aware analysis.
