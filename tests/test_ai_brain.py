from atlas.core.ai_brain import FreeFirstBrain
from atlas.core.config import configured_provider_names, default_settings
from atlas.core.orchestrator import AtlasOrchestrator
from atlas.modules.voice_engine import VoiceEngine


def test_settings_include_free_first_gemini_and_groq_slots() -> None:
    settings = default_settings()
    names = [provider.name for provider in settings.llm_options]

    assert "gemini" in names
    assert "groq" in names
    assert settings.preferred_llm == "gemini"
    assert settings.voice_gender == "female"
    assert settings.secondary_languages == ("hi", "ur")


def test_configured_providers_use_api_keys_when_present() -> None:
    settings = default_settings()
    env = {"GEMINI_API_KEY": "yes", "GROQ_API_KEY": "yes"}

    configured = [provider.name for provider in settings.llm_options if provider.is_configured(env)]

    assert "gemini" in configured
    assert "groq" in configured
    assert "ollama" in configured_provider_names(settings.llm_options)


def test_free_first_brain_maps_flexible_volume_command() -> None:
    intent = FreeFirstBrain().plan("please lower the sound a little")

    assert intent.name == "volume_control"
    assert intent.args["level"] == 35
    assert intent.args["planned_by"] == "free_first_brain"


def test_orchestrator_uses_brain_for_unknown_natural_command() -> None:
    response = AtlasOrchestrator().execute_text("please find online linux voice assistant")

    assert response.ok is True
    assert response.intent == "web_search"
    assert response.data["query"] == "linux voice assistant"


def test_orchestrator_keeps_unknown_when_brain_has_no_plan() -> None:
    response = AtlasOrchestrator().execute_text("paint the moon purple")

    assert response.ok is False
    assert response.intent == "unknown"


def test_voice_plan_names_female_bilingual_defaults() -> None:
    plan = VoiceEngine().describe_voice_plan()

    assert "female" in plan.casefold()
    assert "Hindi" in plan
    assert "Urdu" in plan
