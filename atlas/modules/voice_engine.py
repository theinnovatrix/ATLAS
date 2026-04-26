"""
Module: atlas.modules.voice_engine
Purpose: Free-first voice provider selection and speech placeholders.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: atlas.core.config
Last Updated: 2026-04-26
"""

from __future__ import annotations

from atlas.core.config import AtlasSettings, configured_provider_names, default_settings


class VoiceEngine:
    """Describe and select Atlas speech providers."""

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

    def describe_voice_plan(self) -> str:
        """Return the Atlas bilingual female voice strategy."""
        return (
            "Atlas defaults to free/local speech: Faster-Whisper for English, Hindi, and Urdu "
            "STT; Piper or Edge TTS for female voice output; ElevenLabs remains an optional "
            "premium upgrade for matching the reference voice later."
        )

    def speak_text(self, text: str) -> str:
        """Return text prepared for TTS playback in this foundation build."""
        cleaned = " ".join(text.split())
        return f"Atlas would speak with the configured female voice: {cleaned}"
