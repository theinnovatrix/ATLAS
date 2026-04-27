from pathlib import Path

from atlas.models import Intent
from atlas.modules.system_control import CommandRunner, SystemControl


def _intent(name: str, **args: object) -> Intent:
    return Intent(name=name, category="system", confidence=1.0, args=args)


def test_volume_command_is_prepared_without_confirmation() -> None:
    control = SystemControl(runner=CommandRunner(available_commands={"amixer"}))

    response = control.volume(_intent("volume_control", level=42))

    assert response.ok is False
    assert response.requires_confirmation is True
    assert response.data["command"] == ["amixer", "set", "Master", "42%"]


def test_volume_command_executes_after_confirmation() -> None:
    runner = CommandRunner(available_commands={"amixer"}, execute=True)
    control = SystemControl(runner=runner)

    response = control.volume(_intent("volume_control", level=42, confirmed=True))

    assert response.ok is True
    assert response.data["executed"] is True
    assert runner.executed_commands == (("amixer", "set", "Master", "42%"),)


def test_app_launch_uses_allowlist() -> None:
    control = SystemControl(runner=CommandRunner(available_commands={"firefox"}))

    response = control.launch_app(_intent("app_launcher", app="firefox"))

    assert response.requires_confirmation is True
    assert response.data["command"] == ["firefox"]


def test_app_launch_blocks_unknown_app() -> None:
    control = SystemControl()

    response = control.launch_app(_intent("app_launcher", app="totally-unknown-app"))

    assert response.ok is False
    assert "allowlist" in response.message


def test_dependency_diagnostics_reports_known_tools() -> None:
    control = SystemControl(runner=CommandRunner(available_commands={"amixer", "xdg-open"}))

    response = control.dependency_diagnostics(_intent("system_diagnostics"))

    assert response.ok is True
    assert response.data["tools"]["amixer"] is True
    assert response.data["tools"]["brightnessctl"] is False


def test_notification_command_is_confirmable() -> None:
    control = SystemControl(runner=CommandRunner(available_commands={"notify-send"}))

    response = control.notify(_intent("notifications", target="hello"))

    assert response.requires_confirmation is True
    assert response.data["command"] == ["notify-send", "Atlas", "hello"]


def test_screenshot_command_uses_target_path(tmp_path: Path) -> None:
    control = SystemControl(runner=CommandRunner(available_commands={"gnome-screenshot"}))
    target = tmp_path / "screen.png"

    response = control.screenshot(_intent("screenshot", target=str(target)))

    assert response.requires_confirmation is True
    assert response.data["command"] == ["gnome-screenshot", "-f", str(target)]
