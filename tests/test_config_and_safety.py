"""
Module: tests.test_config_and_safety
Purpose: Validate Atlas free-first provider settings and safety policy.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: pytest
Last Updated: 2026-04-26
"""

from atlas.core.config import configured_provider_names, default_settings
from atlas.core.safety import CONFIRMATION_TOKEN, SafetyPolicy
from atlas.models import RiskLevel


class DummyCapability:
    """Small test capability object."""

    def __init__(self, name: str, risk: RiskLevel) -> None:
        self.name = name
        self.risk = risk


def test_free_first_provider_defaults_are_available() -> None:
    """Atlas should start with free/offline providers configured."""
    settings = default_settings()

    assert settings.assistant_name == "Atlas"
    assert settings.persona == "bilingual female desktop cognitive engine"
    assert "ollama" in configured_provider_names(settings.llm_options)
    assert "faster-whisper" in configured_provider_names(settings.stt_options)
    assert "piper" in configured_provider_names(settings.tts_options)
    assert "edge-tts" in configured_provider_names(settings.tts_options)


def test_confirm_risk_requires_token() -> None:
    """Risky capabilities require the Atlas confirmation token."""
    policy = SafetyPolicy()
    capability = DummyCapability("volume_control", RiskLevel.CONFIRM)

    decision = policy.evaluate(capability)

    assert decision.allowed is False
    assert decision.requires_confirmation is True


def test_confirm_risk_allows_token() -> None:
    """Confirmation token should allow a confirm-level capability."""
    policy = SafetyPolicy()
    capability = DummyCapability("volume_control", RiskLevel.CONFIRM)

    decision = policy.evaluate(capability, CONFIRMATION_TOKEN)

    assert decision.allowed is True


def test_dangerous_capability_is_blocked_even_with_token() -> None:
    """Dangerous capabilities stay blocked."""
    policy = SafetyPolicy()
    capability = DummyCapability("private_backend_scrape", RiskLevel.DANGEROUS)

    decision = policy.evaluate(capability, CONFIRMATION_TOKEN)

    assert decision.allowed is False
    assert decision.risk == RiskLevel.DANGEROUS
