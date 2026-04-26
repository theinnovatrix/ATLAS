"""
Module: atlas.core.safety
Purpose: Apply risk labels and confirmation rules before Atlas executes commands.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library
Last Updated: 2026-04-26
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Protocol

from atlas.models import RiskLevel


CONFIRMATION_TOKEN = "CONFIRM_ATLAS_ACTION"


class SafetyCapability(Protocol):
    """Capability fields consumed by safety evaluation."""

    name: str
    risk: RiskLevel


@dataclass(frozen=True)
class SafetyDecision:
    """Decision returned by the safety policy."""

    allowed: bool
    risk: RiskLevel
    message: str
    requires_confirmation: bool = False


class SafetyPolicy:
    """Guard privileged, destructive, or unsupported Atlas capabilities."""

    def __init__(self, safe_mode: bool = True) -> None:
        """Initialize the policy.

        Args:
            safe_mode: When true, risky operations require an explicit token.
        """
        self.safe_mode = safe_mode
        self._dangerous_intents = {
            "private_backend_scrape",
            "bypass_login",
            "disable_security",
            "run_untrusted_code",
        }

    def evaluate(
        self, capability: SafetyCapability, confirmation_token: str | None = None
    ) -> SafetyDecision:
        """Return whether a capability is allowed to execute."""
        if capability.name in self._dangerous_intents or capability.risk == RiskLevel.DANGEROUS:
            return SafetyDecision(
                allowed=False,
                risk=RiskLevel.DANGEROUS,
                message=(
                    "Atlas cannot bypass authentication, access private backends, "
                    "disable security controls, or run untrusted code."
                ),
            )
        if capability.risk == RiskLevel.CONFIRM and self.safe_mode:
            if confirmation_token == CONFIRMATION_TOKEN:
                return SafetyDecision(
                    allowed=True,
                    risk=RiskLevel.CONFIRM,
                    message="Confirmed risky action.",
                )
            return SafetyDecision(
                allowed=False,
                risk=RiskLevel.CONFIRM,
                message=f"This action requires confirmation token {CONFIRMATION_TOKEN}.",
                requires_confirmation=True,
            )
        if capability.risk == RiskLevel.UNSUPPORTED:
            return SafetyDecision(
                allowed=False,
                risk=RiskLevel.UNSUPPORTED,
                message="Atlas does not understand that command yet.",
            )
        return SafetyDecision(allowed=True, risk=capability.risk, message="Allowed.")
