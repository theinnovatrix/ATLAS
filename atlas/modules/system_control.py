"""
Module: atlas.modules.system_control
Purpose: Safe Linux system information and allowlisted control helpers.
Author: NOVA Development Agent
Version: 0.4.0
Dependencies: standard library
Last Updated: 2026-04-27
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any, Protocol

from atlas.models import AssistantResponse, Intent, RiskLevel


SYSTEM_EXECUTABLES = (
    "amixer",
    "brightnessctl",
    "xdg-open",
    "notify-send",
    "loginctl",
    "gnome-screenshot",
)

APP_ALLOWLIST = {
    "browser": ("xdg-open", "https://duckduckgo.com"),
    "firefox": ("firefox",),
    "chrome": ("google-chrome",),
    "terminal": ("gnome-terminal",),
    "files": ("xdg-open", str(Path.home())),
    "calculator": ("gnome-calculator",),
    "settings": ("gnome-control-center",),
}


@dataclass(frozen=True)
class CommandPlan:
    """Allowlisted system command plan."""

    command: tuple[str, ...]
    description: str


class CommandRunnerProtocol(Protocol):
    """Small command runner interface for local and mocked execution."""

    def which(self, executable: str) -> str | None:
        """Return executable path if available."""

    def popen(self, command: list[str]) -> None:
        """Start a command without blocking."""


@dataclass
class CommandRunner:
    """Deterministic command runner for tests and dry-run checks."""

    available_commands: set[str]
    execute: bool = False
    executed_commands: tuple[tuple[str, ...], ...] = ()

    def which(self, executable: str) -> str | None:
        """Return a fake executable path when the command is available."""
        if executable in self.available_commands:
            return f"/usr/bin/{executable}"
        return None

    def popen(self, command: list[str]) -> None:
        """Record a command when execution is enabled."""
        if not self.execute:
            return
        self.executed_commands = (*self.executed_commands, tuple(command))


class LocalCommandRunner:
    """Run allowlisted commands on the local Linux desktop."""

    def which(self, executable: str) -> str | None:
        """Return executable path if available."""
        return shutil.which(executable)

    def popen(self, command: list[str]) -> None:
        """Start a command without blocking."""
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SystemControl:
    """Provide Linux capabilities through strict command allowlists."""

    def __init__(self, runner: CommandRunnerProtocol | None = None) -> None:
        """Initialize with an injectable command runner for tests."""
        self.runner = runner or LocalCommandRunner()

    def system_info(self, intent: Intent) -> AssistantResponse:
        """Return basic PC details."""
        load = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
        data: dict[str, Any] = {
            "assistant": "Atlas",
            "os": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or "unknown",
            "python": platform.python_version(),
            "cpu_count": os.cpu_count() or 0,
            "load_average": tuple(round(value, 2) for value in load),
            "desktop_session": os.environ.get("XDG_SESSION_TYPE", "unknown"),
        }
        return AssistantResponse(
            ok=True,
            message=(
                f"Atlas is running on {data['os']} with {data['cpu_count']} CPU cores "
                f"and Python {data['python']}."
            ),
            intent=intent.name,
            data=data,
        )

    def diagnostics(self, intent: Intent) -> AssistantResponse:
        """Return system-control command availability."""
        commands = {name: self.runner.which(name) is not None for name in SYSTEM_EXECUTABLES}
        return AssistantResponse(
            ok=True,
            message="System control diagnostics ready.",
            intent=intent.name,
            data={
                "commands": commands,
                "desktop_session": os.environ.get("XDG_SESSION_TYPE", "unknown"),
                "supported_apps": sorted(APP_ALLOWLIST),
            },
        )

    def dependency_diagnostics(self, intent: Intent) -> AssistantResponse:
        """Compatibility wrapper for dependency diagnostics."""
        response = self.diagnostics(intent)
        return AssistantResponse(
            response.ok,
            response.message,
            response.intent,
            response.risk,
            {**response.data, "tools": response.data["commands"]},
            response.requires_confirmation,
        )

    def service_status(self, intent: Intent) -> AssistantResponse:
        """Return a safe systemd status command plan instead of executing it."""
        service = str(intent.args.get("target", "ssh")).strip() or "ssh"
        plan = CommandPlan(("systemctl", "status", service), f"Check service status for {service}.")
        return AssistantResponse(
            ok=True,
            message=plan.description,
            intent=intent.name,
            data={"command": list(plan.command), "executed": False},
        )

    def temperature(self, intent: Intent) -> AssistantResponse:
        """Return thermal information when Linux exposes it."""
        thermal_paths = sorted(Path("/sys/class/thermal").glob("thermal_zone*/temp"))
        readings: list[str] = []
        for path in thermal_paths[:8]:
            try:
                celsius = int(path.read_text(encoding="utf-8").strip()) / 1000
            except (OSError, ValueError):
                continue
            readings.append(f"{path.parent.name}: {celsius:.1f} C")

        if not readings:
            return AssistantResponse(
                ok=False,
                message="I could not read temperature sensors on this machine.",
                intent=intent.name,
            )
        return AssistantResponse(
            ok=True,
            message="Temperature readings: " + "; ".join(readings),
            intent=intent.name,
            data={"readings": readings},
        )

    def volume(self, intent: Intent) -> AssistantResponse:
        """Prepare or run an allowlisted volume command."""
        action = str(intent.args.get("action", "")).strip()
        if action in {"mute", "unmute"}:
            plan = CommandPlan(("amixer", "set", "Master", action), f"{action.title()} volume.")
            return self._confirmable_command(intent, plan)

        level = int(intent.args.get("level", 50))
        level = max(0, min(100, level))
        plan = CommandPlan(("amixer", "set", "Master", f"{level}%"), f"Set volume to {level}%.")
        return self._confirmable_command(intent, plan)

    def brightness(self, intent: Intent) -> AssistantResponse:
        """Prepare or run an allowlisted brightness command."""
        level = int(intent.args.get("level", 50))
        level = max(1, min(100, level))
        plan = CommandPlan(("brightnessctl", "set", f"{level}%"), f"Set brightness to {level}%.")
        return self._confirmable_command(intent, plan)

    def launch_app(self, intent: Intent) -> AssistantResponse:
        """Prepare or run an allowlisted app launch command."""
        app = str(intent.args.get("app") or "").strip().lower()
        if not app:
            return AssistantResponse(False, "Tell me which app to open.", intent.name)
        if app not in APP_ALLOWLIST:
            return AssistantResponse(
                False,
                f"'{app}' is not in the Atlas app allowlist.",
                intent.name,
                RiskLevel.CONFIRM,
                data={"supported_apps": sorted(APP_ALLOWLIST)},
            )
        plan = CommandPlan(APP_ALLOWLIST[app], f"Launch {app}.")
        return self._confirmable_command(intent, plan)

    def open_path(self, intent: Intent) -> AssistantResponse:
        """Prepare or run a command to open a file or folder."""
        raw_path = str(intent.args.get("path") or intent.args.get("target") or "").strip()
        path = Path(raw_path).expanduser() if raw_path else Path.home()
        plan = CommandPlan(("xdg-open", str(path)), f"Open {path}.")
        return self._confirmable_command(intent, plan)

    def notify(self, intent: Intent) -> AssistantResponse:
        """Prepare or run a desktop notification."""
        text = str(intent.args.get("target", "")).strip() or "Atlas notification"
        plan = CommandPlan(("notify-send", "Atlas", text), f"Send notification: {text}")
        return self._confirmable_command(intent, plan)

    def screenshot(self, intent: Intent) -> AssistantResponse:
        """Prepare or run a screenshot command."""
        raw_path = str(intent.args.get("target", "")).strip()
        path = Path(raw_path).expanduser() if raw_path else Path.home() / "Pictures" / "atlas-screenshot.png"
        plan = CommandPlan(("gnome-screenshot", "-f", str(path)), f"Save screenshot to {path}.")
        return self._confirmable_command(intent, plan)

    def lock_screen(self, intent: Intent) -> AssistantResponse:
        """Prepare a lock-screen command."""
        plan = CommandPlan(("loginctl", "lock-session"), "Lock the screen.")
        return self._confirmable_command(intent, plan)

    def _confirmable_command(self, intent: Intent, plan: CommandPlan) -> AssistantResponse:
        """Return command metadata; execute only when confirmation is explicit."""
        command = list(plan.command)
        executable = command[0]
        if self.runner.which(executable) is None:
            return AssistantResponse(
                ok=False,
                message=f"{executable} is not installed or not available in PATH.",
                intent=intent.name,
                risk=RiskLevel.CONFIRM,
                data={"command": command, "executed": False},
            )
        if intent.args.get("confirmed") is True:
            try:
                self.runner.popen(command)
            except OSError as error:
                return AssistantResponse(
                    ok=False,
                    message=f"Failed to run {executable}: {error}",
                    intent=intent.name,
                    risk=RiskLevel.CONFIRM,
                    data={"command": command, "executed": False},
                )
            return AssistantResponse(
                ok=True,
                message=plan.description,
                intent=intent.name,
                risk=RiskLevel.CONFIRM,
                data={"command": command, "executed": True},
            )
        return AssistantResponse(
            ok=False,
            message=f"Confirmation required before I run: {' '.join(command)}",
            intent=intent.name,
            risk=RiskLevel.CONFIRM,
            data={"command": command, "executed": False, "confirmation_hint": "--confirm"},
            requires_confirmation=True,
        )
