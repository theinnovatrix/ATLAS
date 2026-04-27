"""
Module: atlas.modules.voice_engine
Purpose: Free-first voice provider selection and speech output adapters.
Author: NOVA Development Agent
Version: 0.2.0
Dependencies: standard library, atlas.core.config
Last Updated: 2026-04-27
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import shutil
import subprocess

from atlas.core.config import AtlasSettings, configured_provider_names, default_settings


@dataclass(frozen=True)
class VoiceOutput:
    """Result from preparing or running speech output."""

    ok: bool
    provider: str
    message: str
    command: list[str] | None = None


class VoiceEngine:
    """Describe, select, and run Atlas speech providers when available."""

    def __init__(self, settings: AtlasSettings | None = None) -> None:
        """Initialize with free/offline defaults and paid upgrade slots."""
        self.settings = settings or default_settings()

    def provider_summary(self) -> dict[str, list[str]]:
        """Return currently usable providers for LLM, STT, TTS, and search."""
        return {
            "llm": configured_provider_names(self.settings.llm_options),
            "stt": configured_provider_names(self.settings.stt_options),
            "tts": configured_provider_names(self.settings.tts_options),
            "search": configured_provider_names(self.settings.search_options),
        }

    def runtime_status(self) -> dict[str, bool | list[str]]:
        """Return installed runtime support for voice output providers."""
        return {
            "configured_tts": self.provider_summary()["tts"],
            "piper_binary": shutil.which("piper") is not None,
            "edge_tts_module": importlib.util.find_spec("edge_tts") is not None,
            "elevenlabs_module": importlib.util.find_spec("elevenlabs") is not None,
        }

    def describe_voice_plan(self) -> str:
        """Return the Atlas bilingual female voice strategy."""
        return (
            "Atlas defaults to free/local speech: Faster-Whisper for English, Hindi, and Urdu "
            "STT; Piper or Edge TTS for female voice output; ElevenLabs remains an optional "
            "premium upgrade for matching the reference voice later."
        )

    def speak_text(self, text: str, execute: bool = False) -> VoiceOutput:
        """Prepare text for TTS playback and optionally run a local provider.

        Args:
            text: Text Atlas should speak.
            execute: When true, run the first available local TTS command.

        Returns:
            VoiceOutput describing the provider and command.
        """
        cleaned = " ".join(text.split())
        if not cleaned:
            return VoiceOutput(False, "none", "Tell Atlas what to say.")

        piper = shutil.which("piper")
        if piper:
            command = [piper, "--output-raw"]
            if execute:
                completed = subprocess.run(
                    command,
                    input=cleaned,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if completed.returncode != 0:
                    return VoiceOutput(False, "piper", completed.stderr.strip(), command)
            return VoiceOutput(True, "piper", f"Prepared Piper female/offline TTS text: {cleaned}", command)

        if importlib.util.find_spec("edge_tts") is not None:
            command = ["python", "-m", "edge_tts", "--voice", "en-US-AriaNeural", "--text", cleaned]
            if execute:
                completed = subprocess.run(command, capture_output=True, text=True, check=False)
                if completed.returncode != 0:
                    return VoiceOutput(False, "edge-tts", completed.stderr.strip(), command)
            return VoiceOutput(True, "edge-tts", f"Prepared Edge female voice text: {cleaned}", command)

        return VoiceOutput(
            True,
            "text-preview",
            f"Atlas would speak with the configured female voice: {cleaned}",
            None,
        )
