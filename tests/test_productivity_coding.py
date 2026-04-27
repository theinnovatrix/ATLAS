from pathlib import Path
import subprocess

from atlas.core.orchestrator import AtlasOrchestrator
from atlas.modules.coding_assistant import CodingAssistant
from atlas.modules.desktop_manager import DesktopManager
from atlas.modules.productivity import ProductivityTools


def test_desktop_copy_path_and_archives(tmp_path: Path) -> None:
    manager = DesktopManager()
    source = tmp_path / "file.txt"
    source.write_text("hello", encoding="utf-8")

    copied = manager.copy_path(str(source))
    archive_message = manager.zip_files(str(source))

    assert copied.endswith("file.txt")
    assert source.with_suffix(".zip").exists()
    assert "Created archive" in archive_message


def test_quick_note_supports_custom_directory(tmp_path: Path) -> None:
    message = DesktopManager().quick_note("remember this", notes_dir=tmp_path)

    assert "Saved note" in message
    assert list(tmp_path.glob("note_*.md"))[0].read_text(encoding="utf-8") == "remember this\n"


def test_productivity_persistent_todos(tmp_path: Path) -> None:
    store = tmp_path / "todos.json"
    tools = ProductivityTools(todo_path=store)

    assert "Added todo" in tools.add_todo("ship milestone six")
    assert "ship milestone six" in tools.list_todos()

    reloaded = ProductivityTools(todo_path=store)
    assert "ship milestone six" in reloaded.list_todos()


def test_coding_assistant_read_only_git_status(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    assistant = CodingAssistant()

    status = assistant.git_status(repo)

    assert status["ok"] is True
    assert status["repo"] == str(repo)


def test_shell_suggestions_do_not_execute() -> None:
    suggestion = CodingAssistant().shell_suggestion("list files")

    assert suggestion["command"] == 'python -m atlas.cli "system diagnostics" --json'
    assert suggestion["execute"] is False


def test_orchestrator_routes_milestone_6_commands() -> None:
    orchestrator = AtlasOrchestrator()

    assert orchestrator.execute_text("copy path README.md").intent == "copy_path"
    assert orchestrator.execute_text("git status").intent == "git_status"
    assert orchestrator.execute_text("suggest command list files").intent == "safe_shell"
    assert orchestrator.execute_text('validate json {"ok": true}').intent == "json_validator"
    assert orchestrator.execute_text("pomodoro 15").intent == "pomodoro_timer"
