"""
Module: atlas.modules.system_control
Purpose: Safe Linux system information and allowlisted control helpers.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library
Last Updated: 2026-04-26
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from atlas.models import AssistantResponse, Intent, RiskLevel


class SystemControl:
    """Provide first-pass system capabilities without requiring heavyweight dependencies."""

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
        """Prepare an allowlisted volume command."""
        level = int(intent.args.get("level", 50))
        level = max(0, min(100, level))
        command = ["amixer", "set", "Master", f"{level}%"]
        return self._confirmable_command(intent, command, f"Set volume to {level}%.")

    def brightness(self, intent: Intent) -> AssistantResponse:
        """Prepare an allowlisted brightness command."""
        level = int(intent.args.get("level", 50))
        level = max(1, min(100, level))
        command = ["brightnessctl", "set", f"{level}%"]
        return self._confirmable_command(intent, command, f"Set brightness to {level}%.")

    def launch_app(self, intent: Intent) -> AssistantResponse:
        """Prepare an allowlisted app launch command."""
        app = str(intent.args.get("app") or "").strip().lower()
        app_map = {
            "browser": "xdg-open",
            "firefox": "firefox",
            "chrome": "google-chrome",
            "terminal": "gnome-terminal",
            "files": "xdg-open",
            "calculator": "gnome-calculator",
        }
        executable = app_map.get(app, app)
        if not executable:
            return AssistantResponse(False, "Tell me which app to open.", intent.name)
        command = [executable]
        if app == "files":
            command.append(str(Path.home()))
        return self._confirmable_command(intent, command, f"Launch {app}.")

    def open_path(self, intent: Intent) -> AssistantResponse:
        """Prepare a command to open a file or folder."""
        raw_path = str(intent.args.get("path") or "").strip()
        path = Path(raw_path).expanduser() if raw_path else Path.home()
        return self._confirmable_command(intent, ["xdg-open", str(path)], f"Open {path}.")

    def lock_screen(self, intent: Intent) -> AssistantResponse:
        """Prepare a lock-screen command."""
        return self._confirmable_command(intent, ["loginctl", "lock-session"], "Lock the screen.")

    @staticmethod
    def _confirmable_command(intent: Intent, command: list[str], message: str) -> AssistantResponse:
        """Return command metadata; execute only when confirmation is explicit."""
        executable = command[0]
        if shutil.which(executable) is None:
            return AssistantResponse(
                ok=False,
                message=f"{executable} is not installed or not available in PATH.",
                intent=intent.name,
                risk=RiskLevel.CONFIRM,
                data={"command": command},
            )
        if intent.args.get("confirmed") is True:
            try:
                subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError as error:
                return AssistantResponse(
                    ok=False,
                    message=f"Failed to run {executable}: {error}",
                    intent=intent.name,
                    risk=RiskLevel.CONFIRM,
                    data={"command": command},
                )
            return AssistantResponse(
                ok=True,
                message=message,
                intent=intent.name,
                risk=RiskLevel.CONFIRM,
                data={"command": command, "executed": True},
            )
        return AssistantResponse(
            ok=False,
            message=f"Confirmation required before I run: {' '.join(command)}",
            intent=intent.name,
            risk=RiskLevel.CONFIRM,
            data={"command": command, "confirmation_hint": "--confirm"},
            requires_confirmation=True,
        )
