# Atlas Milestone 7

Milestone 7 adds the first desktop GUI foundation. The GUI is optional and uses
PyQt6 when installed, while the controller remains testable without GUI
dependencies.

## Implemented now

- `AtlasGuiController` for command execution, transcript tracking, and status
  updates.
- Lazy PyQt6 main window with a futuristic dark dashboard, command rail,
  status cards, chat transcript, command input, send button, and quick actions.
- `atlas-gui` console entry point.
- Graceful message when PyQt6 is not installed.
- Tests for controller behavior and GUI fallback.

## Try it

```bash
python -m pip install -e ".[gui]"
atlas-gui
```

If PyQt6 is not installed, Atlas prints setup instructions instead of crashing.

## Next work

- Add worker threads for long-running commands.
- Add settings and API-key panels.
- Add animated status/audio indicators and tray integration.
