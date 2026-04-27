from atlas.gui.controller import AtlasGuiController, ChatMessage
from atlas.gui_app import main
from atlas.gui.main_window import pyqt_available


def test_controller_starts_with_welcome_message() -> None:
    controller = AtlasGuiController()

    assert controller.history
    assert controller.history[0].sender == "Atlas"


def test_controller_sends_command_and_records_response() -> None:
    controller = AtlasGuiController()

    response = controller.send_command("define atlas")

    assert response.ok is True
    assert controller.history[-2] == ChatMessage("You", "define atlas")
    assert "local-first" in controller.history[-1].text


def test_controller_serializes_history() -> None:
    controller = AtlasGuiController()
    controller.send_command("what can you do")

    serialized = controller.serialized_history()

    assert serialized[0]["sender"] == "Atlas"
    assert serialized[-1]["sender"] == "Atlas"


def test_pyqt_availability_probe_returns_boolean() -> None:
    assert isinstance(pyqt_available(), bool)


def test_gui_console_entrypoint_imports() -> None:
    assert callable(main)


def test_controller_transcript_text_uses_atlas_branding() -> None:
    controller = AtlasGuiController()

    assert controller.transcript_text().startswith("Atlas:")
