from atlas.core.orchestrator import AtlasOrchestrator


def test_todo_alias_adds_item() -> None:
    response = AtlasOrchestrator().execute_text("add todo buy milk")

    assert response.ok is True
    assert response.intent == "todo_list"
    assert "buy milk" in response.message


def test_timer_alias_extracts_minutes() -> None:
    response = AtlasOrchestrator().execute_text("set timer 12 minutes")

    assert response.ok is True
    assert response.intent == "timer"
    assert "12 minutes" in response.message


def test_dictionary_alias_extracts_word() -> None:
    response = AtlasOrchestrator().execute_text("define atlas")

    assert response.ok is True
    assert response.intent == "dictionary"
    assert "local-first" in response.message


def test_unknown_command_returns_suggestions() -> None:
    response = AtlasOrchestrator().execute_text("desktop cleanup magic")

    assert response.ok is False
    assert response.intent == "unknown"
    assert response.data["suggestions"]


def test_confirmation_response_includes_cli_hint() -> None:
    response = AtlasOrchestrator().execute_text("brightness 20")

    assert response.ok is False
    assert response.requires_confirmation is True
    assert response.data["confirmation_flag"] == "--confirm"
