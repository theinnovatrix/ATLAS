"""
Module: atlas.models
Purpose: Shared structured result and intent models for Atlas.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: dataclasses, enum
Last Updated: 2026-04-26
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    """Safety level assigned to an assistant capability."""

    SAFE = "safe"
    CONFIRM = "confirm"
    DANGEROUS = "dangerous"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class Intent:
    """Parsed command intent and extracted arguments."""

    name: str
    category: str
    confidence: float
    language: str = "en"
    args: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


@dataclass(frozen=True)
class AssistantResponse:
    """Structured response returned by Atlas command execution."""

    ok: bool
    message: str
    intent: str
    risk: RiskLevel = RiskLevel.SAFE
    data: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass(frozen=True)
class Capability:
    """A feature Atlas can route to, execute, or report as planned."""

    name: str
    category: str
    description: str
    status: str
    risk: RiskLevel = RiskLevel.SAFE
    aliases: tuple[str, ...] = ()

