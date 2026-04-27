from atlas.core.intent_parser import IntentParser
from atlas.core.orchestrator import AtlasOrchestrator
from atlas.modules.audio_processor import AudioProcessor
from atlas.modules.voice_engine import VoiceEngine


def test_voice_status_reports_provider_diagnostics() -> None:
    response = AtlasOrchestrator().execute_text("voice status")

    assert response.ok is True
    assert response.intent == "voice_status"
    assert "stt" in response.data
    assert "tts" in response.data
    assert "audio" in response.data


def test_say_text_uses_voice_engine_preview() -> None:
    response = AtlasOrchestrator().execute_text("say hello Atlas")

    assert response.ok is True
    assert response.intent == "text_to_speech"
    assert "hello atlas" in response.message.casefold()


def test_transcribe_file_reports_missing_file(tmp_path) -> None:
    missing = tmp_path / "not-here.wav"
    response = AtlasOrchestrator().execute_text(f"transcribe {missing}")

    assert response.ok is False
    assert response.intent == "speech_to_text"
    assert "does not exist" in response.message


def test_voice_parser_extracts_targets() -> None:
    parser = IntentParser()

    assert parser.parse("voice status").name == "voice_status"
    assert parser.parse("say hello").args["target"] == "hello"
    assert parser.parse("transcribe /tmp/audio.wav").args["target"] == "/tmp/audio.wav"


def test_audio_processor_diagnostics_are_structured() -> None:
    diagnostics = AudioProcessor().diagnostics()

    assert isinstance(diagnostics.stt_available, bool)
    assert isinstance(diagnostics.recorder_available, bool)
    assert isinstance(diagnostics.missing_dependencies, tuple)


def test_transcription_requires_existing_audio_file(tmp_path) -> None:
    result = AudioProcessor().transcribe(tmp_path / "definitely-missing.wav")

    assert result.ok is False
    assert "does not exist" in result.message


def test_voice_engine_preview_is_free_first() -> None:
    preview = VoiceEngine().speak_text("  Hello   Atlas  ")

    assert preview.ok is True
    assert preview.provider in {"piper", "edge-tts", "text-preview"}
    assert "Hello Atlas" in preview.message
