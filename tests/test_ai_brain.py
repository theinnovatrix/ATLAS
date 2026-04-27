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


class FakeAIClient:
    """Fake hosted AI HTTP client for tests."""

    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.requests: list[tuple[str, dict[str, object], dict[str, str] | None]] = []

    def post_json(
        self,
        url: str,
        payload: dict[str, object],
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        self.requests.append((url, payload, headers))
        return self.response


def _gemini_response(raw_json: str) -> dict[str, object]:
    return {"candidates": [{"content": {"parts": [{"text": raw_json}]}}]}


def test_hosted_planner_maps_valid_json_intent() -> None:
    client = FakeAIClient(
        _gemini_response(
            '{"intent":"web_search","args":{"target":"linux assistant"},"language":"en"}'
        )
    )
    brain = FreeFirstBrain(
        env={"GEMINI_API_KEY": "key"},
        client=client,
    )

    intent = brain.plan_hosted("do something flexible")

    assert intent is not None
    assert intent.name == "web_search"
    assert intent.args["target"] == "linux assistant"
    assert intent.args["planned_by"] == "gemini"
    assert "generativelanguage.googleapis.com" in client.requests[0][0]


def test_hosted_planner_rejects_disallowed_intent() -> None:
    client = FakeAIClient(
        _gemini_response(
            '{"intent":"private_backend_scrape","args":{},"language":"en"}'
        )
    )
    brain = FreeFirstBrain(
        env={"GEMINI_API_KEY": "key"},
        client=client,
    )

    assert brain.plan_hosted("break rules") is None


def test_hosted_planner_falls_back_to_groq_when_gemini_invalid() -> None:
    class SequenceClient(FakeAIClient):
        def __init__(self) -> None:
            super().__init__({})
            self.responses = [
                _gemini_response("not-json"),
                {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"intent":"dictionary","args":{"target":"atlas"},'
                                    '"language":"en"}'
                                )
                            }
                        }
                    ]
                },
            ]

        def post_json(
            self,
            url: str,
            payload: dict[str, object],
            headers: dict[str, str] | None = None,
        ) -> dict[str, object]:
            self.requests.append((url, payload, headers))
            return self.responses.pop(0)

    client = SequenceClient()
    brain = FreeFirstBrain(env={"GEMINI_API_KEY": "key", "GROQ_API_KEY": "key"}, client=client)

    intent = brain.plan_hosted("what does atlas mean")

    assert intent is not None
    assert intent.name == "dictionary"
    assert intent.args["planned_by"] == "groq"
    assert "api.groq.com" in client.requests[1][0]
