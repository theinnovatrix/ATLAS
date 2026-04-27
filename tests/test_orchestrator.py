from atlas.core.orchestrator import AtlasOrchestrator
from atlas.core.safety import CONFIRMATION_TOKEN


def test_system_info_command_returns_data():
    response = AtlasOrchestrator().execute_text("system info")
    assert response.ok is True
    assert "python" in response.data


def test_calculator_command_executes_safely():
    response = AtlasOrchestrator().execute_text("calculate 2 + 2 * 3")
    assert response.ok is True
    assert response.message == "2 + 2 * 3 = 8"


def test_hindi_weather_command_uses_city_argument():
    response = AtlasOrchestrator().execute_text("mausam Delhi")
    assert response.intent == "weather_info"
    assert response.data["city"] == "delhi"


def test_confirmable_volume_is_blocked_without_token():
    response = AtlasOrchestrator().execute_text("volume 30")
    assert response.ok is False
    assert response.requires_confirmation is True


def test_confirmable_volume_reaches_handler_with_token():
    response = AtlasOrchestrator().execute_text("volume 30", CONFIRMATION_TOKEN)
    assert response.intent == "volume_control"
    assert "command" in response.data
    assert response.data["executed"] in {True, False}
    assert response.requires_confirmation is False


def test_capabilities_lists_registered_features():
    response = AtlasOrchestrator().execute_text("what can you do")
    assert response.ok is True
    assert response.data["registered"] >= 100
    assert response.data["implemented"] >= 20


def test_voice_status_command_reports_diagnostics():
    response = AtlasOrchestrator().execute_text("voice status")
    assert response.ok is True
    assert response.intent == "voice_status"
    assert "audio" in response.data


def test_system_dependencies_route_is_available():
    response = AtlasOrchestrator().execute_text("system dependencies")

    assert response.ok is True
    assert response.intent == "system_diagnostics"
    assert "amixer" in response.data["commands"]


def test_news_route_returns_structured_response():
    response = AtlasOrchestrator().execute_text("news")

    assert response.intent == "daily_news"
    assert "articles" in response.data
