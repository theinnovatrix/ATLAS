"""
Module: atlas.core.config
Purpose: Load Atlas settings with free-first providers and paid upgrade slots.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library
Last Updated: 2026-04-26
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Mapping


@dataclass(frozen=True)
class ProviderOption:
    """Describe an interchangeable AI, STT, TTS, or search provider."""

    name: str
    cost_tier: str
    requires_key: bool
    env_var: str | None = None
    languages: tuple[str, ...] = ("en",)
    notes: str = ""

    def is_configured(self, env: Mapping[str, str] | None = None) -> bool:
        """Return whether this provider can be used with the current environment."""
        values = env or os.environ
        if not self.requires_key:
            return True
        return bool(self.env_var and values.get(self.env_var))


@dataclass(frozen=True)
class AtlasSettings:
    """Runtime settings for Atlas."""

    assistant_name: str = "Atlas"
    default_language: str = "en"
    secondary_languages: tuple[str, ...] = ("hi", "ur")
    persona: str = "bilingual female desktop cognitive engine"
    safe_mode: bool = True
    preferred_llm: str = "ollama"
    preferred_stt: str = "faster-whisper"
    preferred_tts: str = "piper"
    preferred_search: str = "duckduckgo-lite"
    llm_options: tuple[ProviderOption, ...] = field(default_factory=tuple)
    stt_options: tuple[ProviderOption, ...] = field(default_factory=tuple)
    tts_options: tuple[ProviderOption, ...] = field(default_factory=tuple)
    search_options: tuple[ProviderOption, ...] = field(default_factory=tuple)


def default_settings() -> AtlasSettings:
    """Create settings that prefer free or cheap providers before paid upgrades."""
    return AtlasSettings(
        llm_options=(
            ProviderOption(
                name="ollama",
                cost_tier="free_local",
                requires_key=False,
                languages=("en", "hi", "ur"),
                notes="Use local models such as llama3.2 or qwen2.5 when installed.",
            ),
            ProviderOption(
                name="groq",
                cost_tier="free_trial_or_low_cost",
                requires_key=True,
                env_var="GROQ_API_KEY",
                languages=("en", "hi", "ur"),
                notes="Fast hosted inference with a low-cost upgrade path.",
            ),
            ProviderOption(
                name="openrouter",
                cost_tier="free_models_or_low_cost",
                requires_key=True,
                env_var="OPENROUTER_API_KEY",
                languages=("en", "hi", "ur"),
                notes="Can route to free and low-cost hosted models.",
            ),
            ProviderOption(
                name="openai",
                cost_tier="paid_upgrade",
                requires_key=True,
                env_var="OPENAI_API_KEY",
                languages=("en", "hi", "ur"),
                notes="Premium option reserved for later upgrade.",
            ),
        ),
        stt_options=(
            ProviderOption(
                name="faster-whisper",
                cost_tier="free_local",
                requires_key=False,
                languages=("en", "hi", "ur"),
                notes="Offline multilingual speech recognition.",
            ),
            ProviderOption(
                name="groq-whisper",
                cost_tier="free_trial_or_low_cost",
                requires_key=True,
                env_var="GROQ_API_KEY",
                languages=("en", "hi", "ur"),
                notes="Hosted Whisper API option for faster machines or cloud use.",
            ),
        ),
        tts_options=(
            ProviderOption(
                name="piper",
                cost_tier="free_local",
                requires_key=False,
                languages=("en",),
                notes="Default offline voice; choose a female model during setup.",
            ),
            ProviderOption(
                name="edge-tts",
                cost_tier="free",
                requires_key=False,
                languages=("en", "hi", "ur"),
                notes="Free neural voices; use female voices such as en-US-AriaNeural.",
            ),
            ProviderOption(
                name="elevenlabs",
                cost_tier="free_trial_then_paid",
                requires_key=True,
                env_var="ELEVENLABS_API_KEY",
                languages=("en", "hi", "ur"),
                notes="Premium natural female voice upgrade slot.",
            ),
        ),
        search_options=(
            ProviderOption(
                name="duckduckgo-lite",
                cost_tier="free",
                requires_key=False,
                languages=("en", "hi", "ur"),
                notes="Public search fallback with polite rate limits.",
            ),
            ProviderOption(
                name="serpapi",
                cost_tier="free_trial_then_paid",
                requires_key=True,
                env_var="SERPAPI_API_KEY",
                languages=("en",),
                notes="Paid upgrade for structured search results.",
            ),
        ),
    )


def configured_provider_names(options: tuple[ProviderOption, ...]) -> list[str]:
    """Return provider names that are currently usable."""
    return [option.name for option in options if option.is_configured()]
