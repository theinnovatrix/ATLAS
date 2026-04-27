"""
Module: atlas.modules.coding_assistant
Purpose: Safe developer helper operations for Atlas.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library
Last Updated: 2026-04-26
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class CodingAssistant:
    """Provide deterministic coding helpers with conservative execution."""

    def explain_code(self, code: str) -> str:
        """Return a simple explanation of a code snippet."""
        lines = [line for line in code.splitlines() if line.strip()]
        if not lines:
            return "No code was provided."
        if "def " in code:
            return f"This Python snippet defines function logic across {len(lines)} non-empty lines."
        if "class " in code:
            return f"This snippet defines a class across {len(lines)} non-empty lines."
        return f"This snippet contains {len(lines)} non-empty lines of code."

    def suggest_tests(self, feature: str) -> list[str]:
        """Suggest focused tests for a feature."""
        subject = feature.strip() or "the feature"
        return [
            f"test_{subject.replace(' ', '_')}_happy_path",
            f"test_{subject.replace(' ', '_')}_invalid_input",
            f"test_{subject.replace(' ', '_')}_permission_or_dependency_failure",
        ]

    def run_python(self, code: str, timeout_seconds: int = 5) -> dict[str, str | int]:
        """Run a Python snippet in a temporary file with a timeout."""
        with tempfile.TemporaryDirectory() as temp_dir:
            script = Path(temp_dir) / "snippet.py"
            script.write_text(code, encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(script)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def validate_json(self, text: str) -> str:
        """Validate JSON text."""
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            return f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}."
        return "JSON is valid."

    def api_test(self, url: str) -> dict[str, str | int]:
        """Run a simple GET request for a public HTTP API endpoint."""
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return {"error": "Provide a full http or https URL."}
        try:
            request = Request(url, headers={"User-Agent": "AtlasAssistant/0.1"})
            with urlopen(request, timeout=5) as response:
                body = response.read(300).decode("utf-8", errors="replace")
                return {"status": response.status, "body_preview": body}
        except OSError as exc:
            return {"error": str(exc)}

    def read_docs(self, path: Path) -> str:
        """Read a short preview from a documentation file."""
        if not path.exists() or not path.is_file():
            return f"Documentation file not found: {path}"
        return path.read_text(encoding="utf-8", errors="replace")[:500]

    def write_docs(self, topic: str) -> str:
        """Return a documentation outline for a topic."""
        subject = topic.strip() or "Atlas feature"
        return f"# {subject}\n\n## Overview\n\n## Usage\n\n## Safety notes\n"

    def ai_coder(self, prompt: str) -> str:
        """Return a local coding-assistant plan without calling paid providers."""
        subject = prompt.strip() or "the requested change"
        return f"Free-first coding plan for {subject}: inspect files, write tests, implement, run checks."

    def write_tests(self, feature: str) -> str:
        """Return suggested test names for a feature."""
        return "; ".join(self.suggest_tests(feature))

    def git_status(self, repo_path: str = ".") -> dict[str, str | int]:
        """Return read-only git status for a repository."""
        repo = Path(repo_path).expanduser()
        result = _run_command(["git", "status", "--short"], repo, timeout_seconds=5)
        return {"ok": result["returncode"] == 0, "repo": str(repo), **result}

    def git_diff_summary(self, repo_path: str = ".") -> dict[str, str | int]:
        """Return a compact git diff stat."""
        repo = Path(repo_path).expanduser()
        result = _run_command(["git", "diff", "--stat"], repo, timeout_seconds=5)
        return {"ok": result["returncode"] == 0, "repo": str(repo), **result}

    def shell_suggestion(self, request: str) -> dict[str, str | list[str]]:
        """Suggest safe read-only shell commands for common developer requests."""
        normalized = request.casefold().strip()
        suggestions = {
            "list files": ["python -m atlas.cli \"system diagnostics\" --json"],
            "git status": ["git status --short"],
            "run tests": ["python -m pytest -q"],
            "lint": ["python -m flake8 atlas tests"],
            "python version": ["python --version"],
        }
        for key, commands in suggestions.items():
            if key in normalized:
                return {
                    "risk": "safe_read_only",
                    "command": commands[0],
                    "commands": commands,
                    "execute": False,
                }
        return {
            "risk": "review_required",
            "execute": False,
            "commands": [],
            "message": "Atlas only suggests known safe shell commands in this milestone.",
        }

    def run_allowed_command(self, command: str) -> dict[str, str | int]:
        """Run a tiny allowlist of read-only developer commands."""
        allowed = {
            "git status": ["git", "status", "--short"],
            "python version": ["python3", "--version"],
        }
        if command not in allowed:
            return {"error": "Command is not in Atlas allowlist.", "allowed": ", ".join(allowed)}
        completed = subprocess.run(
            allowed[command],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }


def _run_command(command: list[str], cwd: Path, timeout_seconds: int) -> dict[str, str | int]:
    """Run a read-only developer command."""
    completed = subprocess.run(
        command,
        cwd=str(cwd.expanduser()),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
