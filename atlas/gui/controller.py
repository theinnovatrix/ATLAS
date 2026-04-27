"""
Module: atlas.gui.controller
Purpose: Testable GUI controller for Atlas command execution.
Author: NOVA Development Agent
Version: 0.7.0
Dependencies: atlas.core.orchestrator
Last Updated: 2026-04-27
"""

from __future__ import annotations

from dataclasses import dataclass, field

from atlas.core.orchestrator import AtlasOrchestrator
from atlas.core.safety import CONFIRMATION_TOKEN
from atlas.models import AssistantResponse


@dataclass
class ChatMessage:
    """Single chat transcript entry."""

    sender: str
    text: str


@dataclass
class GuiState:
    """State exposed to the GUI widgets."""

    status: str = "Ready"
    transcript: list[ChatMessage] = field(default_factory=list)
    last_response: AssistantResponse | None = None


class AtlasGuiController:
    """Coordinate GUI actions with the Atlas orchestrator."""

    def __init__(self, orchestrator: AtlasOrchestrator | None = None) -> None:
        """Initialize a controller with injectable orchestration."""
        self.orchestrator = orchestrator or AtlasOrchestrator()
        self.state = GuiState()
        self.add_assistant_message("Atlas ready. Type a command or use voice status.")

    def add_user_message(self, text: str) -> None:
        """Append a user message."""
        self.state.transcript.append(ChatMessage("You", text))

    def add_assistant_message(self, text: str) -> None:
        """Append an assistant message."""
        self.state.transcript.append(ChatMessage("Atlas", text))

    @property
    def history(self) -> list[ChatMessage]:
        """Return chat transcript entries."""
        return self.state.transcript

    def send_command(self, text: str, confirmed: bool = False) -> AssistantResponse:
        """Compatibility wrapper for GUI command submission."""
        return self.run_command(text, confirmed)

    def run_command(self, text: str, confirmed: bool = False) -> AssistantResponse:
        """Run a command from the GUI and update transcript state."""
        command = text.strip()
        if not command:
            response = AssistantResponse(False, "Type a command for Atlas.", "empty")
            self.state.last_response = response
            self.state.status = "Waiting for command"
            self.add_assistant_message(response.message)
            return response

        self.add_user_message(command)
        self.state.status = "Running"
        token = CONFIRMATION_TOKEN if confirmed else None
        response = self.orchestrator.execute_text(command, confirmation_token=token)
        self.state.last_response = response
        self.state.status = _status_from_response(response)
        self.add_assistant_message(response.message)
        return response

    def transcript_text(self) -> str:
        """Return transcript as display text."""
        return "\n".join(f"{message.sender}: {message.text}" for message in self.state.transcript)

    def serialized_history(self) -> list[dict[str, str]]:
        """Return transcript as JSON-friendly dictionaries."""
        return [
            {"sender": message.sender, "text": message.text}
            for message in self.state.transcript
        ]


def _status_from_response(response: AssistantResponse) -> str:
    """Map command response to a GUI status label."""
    if response.requires_confirmation:
        return "Confirmation required"
    if response.ok:
        return "Ready"
    return "Error"
