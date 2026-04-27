# Atlas Milestone 7

Milestone 7 adds the first desktop GUI foundation. The GUI is optional and uses
PyQt6 when installed, while the controller remains testable without GUI
dependencies.

## Implemented now

- `AtlasGuiController` for command execution, transcript tracking, and status
  updates.
- Lazy PyQt6 main window with chat transcript, command input, send button,
  quick command buttons, and status label.
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
- Add activity log and tray integration.
