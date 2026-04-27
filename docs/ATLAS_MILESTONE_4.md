# Atlas Milestone 4

Milestone 4 deepens Linux system control while keeping Atlas safe by default.
Commands are allowlisted, confirmation-gated, and tested with mocked runners.

## Implemented now

- Dependency diagnostics for Linux tools such as `amixer`, `brightnessctl`,
  `xdg-open`, `notify-send`, `gnome-screenshot`, and `loginctl`.
- Confirm-gated command planning and execution metadata for volume,
  brightness, app launch, file open, notifications, screenshots, lock screen,
  and service status.
- Injectable command runner so tests can verify subprocess behavior without
  changing the local machine.
- CLI routes:
  - `python -m atlas.cli "system diagnostics"`
  - `python -m atlas.cli "notify hello"`
  - `python -m atlas.cli "screenshot"`
  - `python -m atlas.cli "lock screen"`
  - `python -m atlas.cli "service ssh"`

## Safety boundary

Atlas still requires confirmation for operations that can affect the desktop or
system. Use `--confirm` when you want Atlas to run a confirm-level command.

## Try it

```bash
python -m atlas.cli "system diagnostics"
python -m atlas.cli "notify hello"
python -m atlas.cli "notify hello" --confirm
python -m atlas.cli "screenshot"
python -m atlas.cli "lock screen" --json
python -m atlas.cli "service ssh"
```

## Next work

- Add more DBus-backed desktop integrations.
- Add distro-specific Parrot OS validation.
- Add real desktop-session manual tests for screenshot and notifications.
