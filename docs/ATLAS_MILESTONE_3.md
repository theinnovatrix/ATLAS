 # Atlas Milestone 3

Milestone 3 improves intent parsing and command routing. The goal is to make
Atlas better at understanding natural commands before expanding deeper system
automation.

## Implemented now

- More command aliases for todos, dictionary lookup, timers, voice, and help.
- Slot extraction for todo items, dictionary words, timer minutes, and voice
  targets.
- Unknown-command suggestions based on registered capabilities.
- Confirmation metadata in blocked risky responses, including the `--confirm`
  CLI flag and internal token.
- Tests for parser aliases, unknown intent guidance, and confirmation routing.

## Try it

```bash
python -m atlas.cli "add todo test milestone three"
python -m atlas.cli "define atlas"
python -m atlas.cli "timer 10"
python -m atlas.cli "mute volume"
python -m atlas.cli "open settings"
python -m atlas.cli "make the moon blue" --json
```

## Next work

- Milestone 4 should deepen Linux system control wrappers with mocked
  subprocess and platform tests.
