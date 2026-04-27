"""
Module: atlas.modules.desktop_manager
Purpose: Desktop and file operations for Atlas.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library
Last Updated: 2026-04-26
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
import zipfile


@dataclass(frozen=True)
class PathValidation:
    """Result from validating a user-provided path."""

    ok: bool
    path: Path
    message: str = ""


class DesktopManager:
    """Handle safe desktop and file management operations."""

    def quick_search(self, query: str, root: Path | None = None, limit: int = 10) -> list[str]:
        """Find files whose names contain the query."""
        if not query:
            return []
        base = root or Path.home()
        matches: list[str] = []
        needle = query.lower()
        for path in base.rglob("*"):
            if len(matches) >= limit:
                break
            if needle in path.name.lower():
                matches.append(str(path))
        return matches

    def make_folder(self, path: str) -> str:
        """Create a directory and parents if needed."""
        target = Path(path).expanduser()
        target.mkdir(parents=True, exist_ok=True)
        return f"Folder ready: {target}"

    def create_file(self, path: str, content: str = "") -> str:
        """Create a text file, refusing to overwrite existing files."""
        target = Path(path).expanduser()
        if target.exists():
            return f"File already exists: {target}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"File created: {target}"

    def validate_path(self, path: str, must_exist: bool = False) -> PathValidation:
        """Validate and expand a path for local file operations."""
        raw = path.strip()
        if not raw:
            return PathValidation(False, Path.home(), "Path is required.")
        target = Path(raw).expanduser()
        if must_exist and not target.exists():
            return PathValidation(False, target, f"Path does not exist: {target}")
        return PathValidation(True, target)

    def create_folder(self, path: Path) -> str:
        """Create a directory from a parsed path object."""
        return self.make_folder(str(path))

    def folder_size(self, path: str) -> dict[str, str]:
        """Return a folder size summary."""
        target = Path(path).expanduser()
        total = sum(item.stat().st_size for item in target.rglob("*") if item.is_file())
        return {"path": str(target), "bytes": str(total), "human": _human_bytes(total)}

    def quick_note(self, text: str, notes_dir: Path | None = None) -> str:
        """Save a timestamped local note."""
        directory = notes_dir or Path.home() / "AtlasNotes"
        directory.mkdir(parents=True, exist_ok=True)
        note_path = directory / f"note_{int(time.time())}.md"
        note_path.write_text(text.strip() + "\n", encoding="utf-8")
        return f"Saved note: {note_path}"

    def zip_files(self, source: str, destination: str | None = None) -> str:
        """Compress a file or folder into a zip archive."""
        source_path = Path(source).expanduser()
        target = Path(destination).expanduser() if destination else source_path.with_suffix(".zip")
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            if source_path.is_dir():
                for item in source_path.rglob("*"):
                    if item.is_file():
                        archive.write(item, item.relative_to(source_path.parent))
            else:
                archive.write(source_path, source_path.name)
        return f"Created archive: {target}"

    def unzip_files(self, archive: str, destination: str | None = None) -> str:
        """Extract a zip archive."""
        archive_path = Path(archive).expanduser()
        target = Path(destination).expanduser() if destination else archive_path.with_suffix("")
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as zip_file:
            zip_file.extractall(target)
        return f"Extracted archive to: {target}"

    def downloads_folder(self) -> str:
        """Return the default downloads path."""
        return str(Path.home() / "Downloads")

    def downloads_path(self) -> str:
        """Return the default downloads path for display-only handlers."""
        return self.downloads_folder()

    def go_home(self) -> str:
        """Return the home folder path."""
        return str(Path.home())

    def copy_path(self, path: str) -> str:
        """Return an absolute path for copying by the caller or UI."""
        return str(Path(path).expanduser().resolve())

    def delete_file_to_trash_plan(self, path: str) -> str:
        """Describe a safe delete operation without deleting anything."""
        return f"Confirmation required before moving to trash: {Path(path).expanduser()}"

    def file_summary(self, path: str) -> dict[str, str]:
        """Return metadata for a file or folder."""
        validation = self.validate_path(path, must_exist=True)
        if not validation.ok:
            return {"error": validation.message, "path": str(validation.path)}
        target = validation.path
        if target.is_dir():
            return {
                "path": str(target),
                "type": "directory",
                "children": str(sum(1 for _ in target.iterdir())),
            }
        return {
            "path": str(target),
            "type": "file",
            "bytes": str(target.stat().st_size),
            "human": _human_bytes(target.stat().st_size),
        }


def _human_bytes(value: int) -> str:
    """Format bytes as a compact human-readable string."""
    amount = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.2f} {unit}"
        amount /= 1024
    return f"{amount:.2f} TB"
