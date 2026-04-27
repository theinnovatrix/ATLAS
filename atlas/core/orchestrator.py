"""
Module: atlas.core.orchestrator
Purpose: Route parsed Atlas intents to safe module handlers.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: atlas core and modules
Last Updated: 2026-04-26
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from atlas.capabilities import CAPABILITIES, Capability, capability_by_name, implemented_capabilities
from atlas.core.config import AtlasSettings, default_settings
from atlas.core.intent_parser import IntentParser
from atlas.core.safety import SafetyPolicy
from atlas.models import AssistantResponse, Intent, RiskLevel
from atlas.modules.coding_assistant import CodingAssistant
from atlas.modules.desktop_manager import DesktopManager
from atlas.modules.audio_processor import AudioProcessor
from atlas.modules.productivity import ProductivityTools
from atlas.modules.system_control import SystemControl
from atlas.modules.voice_engine import VoiceEngine
from atlas.modules.web_media import WebMediaManager


class AtlasOrchestrator:
    """Execute Atlas text commands through parser, safety, and modules."""

    def __init__(
        self,
        settings: AtlasSettings | None = None,
        safety: SafetyPolicy | None = None,
    ) -> None:
        """Initialize module handlers."""
        self.settings = settings or default_settings()
        self.parser = IntentParser()
        self.safety = safety or SafetyPolicy()
        self.system = SystemControl()
        self.desktop = DesktopManager()
        self.audio = AudioProcessor()
        self.productivity = ProductivityTools()
        self.web = WebMediaManager()
        self.coding = CodingAssistant()
        self.voice = VoiceEngine(self.settings)
        self.handlers: dict[str, Callable[[Intent], AssistantResponse]] = {
            "system_info": self._system_info,
            "system_diagnostics": self._system_diagnostics,
            "service_status": self._service_status,
            "volume_control": self._volume_control,
            "brightness_control": self._brightness_control,
            "pc_temp_check": self._temperature,
            "app_launcher": self._launch_app,
            "file_opener": self._open_file,
            "screenshot": self._screenshot,
            "notifications": self._notification,
            "lock_screen": self._lock_screen,
            "quick_search": self._quick_search,
            "folder_maker": self._folder_maker,
            "quick_note": self._quick_note,
            "folder_size": self._folder_size,
            "copy_path": self._copy_path,
            "zip_files": self._zip_files,
            "unzip_files": self._unzip_files,
            "downloads_folder": self._downloads_folder,
            "go_home": self._go_home,
            "calendar_view": self._calendar_view,
            "timer": self._timer,
            "pomodoro_timer": self._pomodoro,
            "calculator": self._calculator,
            "unit_converter": self._unit_converter,
            "translate_text": self._translate,
            "dictionary": self._dictionary,
            "todo_list": self._todo,
            "web_search": self._web_search,
            "weather_info": self._weather,
            "daily_news": self._news,
            "youtube_metadata": self._youtube,
            "page_summary": self._page_summary,
            "stock_prices": self._stock_prices,
            "tell_joke": self._joke,
            "daily_quote": self._quote,
            "meditation": self._meditation,
            "workout_plan": self._workout,
            "diet_plan": self._diet,
            "recipes": self._recipe,
            "pet_care": self._pet_care,
            "plant_care": self._plant_care,
            "home_decor": self._home_decor,
            "fashion_tips": self._fashion,
            "makeup_tips": self._makeup,
            "api_tester": self._api_test,
            "explain_code": self._explain_code,
            "git_status": self._git_status,
            "git_diff": self._git_diff,
            "json_validator": self._json_validator,
            "safe_shell": self._safe_shell,
            "read_docs": self._read_docs,
            "write_docs": self._write_docs,
            "ai_coder": self._ai_coder,
            "write_tests": self._write_tests,
            "voice_status": self._voice_status,
            "text_to_speech": self._text_to_speech,
            "speech_to_text": self._speech_to_text,
            "linux_commands": self._linux_command,
            "run_code": self._run_code,
            "capabilities": self._capabilities,
        }

    def execute_text(self, text: str, confirmation_token: str | None = None) -> AssistantResponse:
        """Parse and execute a natural-language command."""
        return self.execute_intent(self.parser.parse(text), confirmation_token)

    def execute_intent(
        self, intent: Intent, confirmation_token: str | None = None
    ) -> AssistantResponse:
        """Execute a parsed intent."""
        capability = capability_by_name(intent.name)
        if capability is None:
            return self._unknown_response(intent)

        safety = self.safety.evaluate(capability, confirmation_token)
        if not safety.allowed:
            return AssistantResponse(
                False,
                safety.message,
                intent.name,
                capability.risk,
                data={
                    "confirmation_token": "CONFIRM_ATLAS_ACTION",
                    "confirmation_flag": "--confirm",
                },
                requires_confirmation=safety.requires_confirmation,
            )
        if confirmation_token is not None:
            intent = Intent(
                name=intent.name,
                category=intent.category,
                confidence=intent.confidence,
                language=intent.language,
                args={**intent.args, "confirmed": True},
                raw_text=intent.raw_text,
            )

        handler = self.handlers.get(intent.name)
        if handler is None:
            count = len(implemented_capabilities())
            return AssistantResponse(
                False,
                (
                    f"{capability.name} is registered but not implemented in this milestone. "
                    f"{count} capabilities have working first-pass handlers."
                ),
                intent.name,
                capability.risk,
            )
        return handler(intent)

    def _system_info(self, intent: Intent) -> AssistantResponse:
        return self.system.system_info(intent)

    def _system_diagnostics(self, intent: Intent) -> AssistantResponse:
        return self.system.diagnostics(intent)

    def _service_status(self, intent: Intent) -> AssistantResponse:
        return self.system.service_status(intent)

    def _volume_control(self, intent: Intent) -> AssistantResponse:
        return self.system.volume(intent)

    def _brightness_control(self, intent: Intent) -> AssistantResponse:
        return self.system.brightness(intent)

    def _temperature(self, intent: Intent) -> AssistantResponse:
        return self.system.temperature(intent)

    def _launch_app(self, intent: Intent) -> AssistantResponse:
        return self.system.launch_app(intent)

    def _open_file(self, intent: Intent) -> AssistantResponse:
        return self.system.open_path(intent)

    def _screenshot(self, intent: Intent) -> AssistantResponse:
        return self.system.screenshot(intent)

    def _notification(self, intent: Intent) -> AssistantResponse:
        return self.system.notify(intent)

    def _lock_screen(self, intent: Intent) -> AssistantResponse:
        return self.system.lock_screen(intent)

    def _quick_search(self, intent: Intent) -> AssistantResponse:
        data = self.desktop.quick_search(str(intent.args.get("target", "")))
        return AssistantResponse(True, f"Found {len(data)} matching paths.", intent.name, data={"paths": data})

    def _folder_maker(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.desktop.make_folder(str(intent.args.get("target", ""))))

    def _quick_note(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.desktop.quick_note(str(intent.args.get("target", ""))))

    def _folder_size(self, intent: Intent) -> AssistantResponse:
        data = self.desktop.folder_size(str(intent.args.get("target", ".")))
        return AssistantResponse(True, f"Folder size: {data['human']}", intent.name, data=data)

    def _copy_path(self, intent: Intent) -> AssistantResponse:
        path = self.desktop.copy_path(str(intent.args.get("target", ".")))
        return AssistantResponse(True, f"Resolved path: {path}", intent.name, data={"path": path})

    def _zip_files(self, intent: Intent) -> AssistantResponse:
        try:
            message = self.desktop.zip_files(str(intent.args.get("target", "")))
        except (FileNotFoundError, OSError, ValueError) as error:
            return AssistantResponse(False, str(error), intent.name)
        return self._message(intent, message)

    def _unzip_files(self, intent: Intent) -> AssistantResponse:
        try:
            message = self.desktop.unzip_files(str(intent.args.get("target", "")))
        except (FileNotFoundError, OSError, ValueError) as error:
            return AssistantResponse(False, str(error), intent.name)
        return self._message(intent, message)

    def _downloads_folder(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, f"Downloads folder: {self.desktop.downloads_folder()}")

    def _go_home(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, f"Home folder: {self.desktop.go_home()}")

    def _calendar_view(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.productivity.calendar_view())

    def _timer(self, intent: Intent) -> AssistantResponse:
        minutes = int(intent.args.get("minutes", 5))
        return self._message(intent, self.productivity.timer(minutes))

    def _pomodoro(self, intent: Intent) -> AssistantResponse:
        minutes = int(intent.args.get("minutes", 25))
        return self._message(intent, self.productivity.pomodoro(minutes))

    def _calculator(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.productivity.calculate(str(intent.args.get("expression", ""))))

    def _unit_converter(self, intent: Intent) -> AssistantResponse:
        value = float(intent.args.get("value", 1))
        return self._message(
            intent,
            self.productivity.unit_convert(
                value,
                str(intent.args.get("from_unit", "km")),
                str(intent.args.get("to_unit", "mi")),
            ),
        )

    def _translate(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.productivity.translate(str(intent.args.get("target", ""))))

    def _dictionary(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.productivity.dictionary(str(intent.args.get("target", ""))))

    def _todo(self, intent: Intent) -> AssistantResponse:
        target = str(intent.args.get("target", "")).strip()
        if target:
            return self._message(intent, self.productivity.add_todo(target))
        return self._message(intent, self.productivity.list_todos())

    def _web_search(self, intent: Intent) -> AssistantResponse:
        return self.web.web_search(str(intent.args.get("target", "")))

    def _weather(self, intent: Intent) -> AssistantResponse:
        return self.web.weather(str(intent.args.get("target", "London")))

    def _news(self, intent: Intent) -> AssistantResponse:
        return self.web.daily_news(str(intent.args.get("target", "general")))

    def _youtube(self, intent: Intent) -> AssistantResponse:
        return self.web.youtube_metadata(str(intent.args.get("target", "")))

    def _page_summary(self, intent: Intent) -> AssistantResponse:
        return self.web.summarize_public_page(str(intent.args.get("target", "")))

    def _stock_prices(self, intent: Intent) -> AssistantResponse:
        return self.web.stock_prices(str(intent.args.get("target", "")))

    def _joke(self, intent: Intent) -> AssistantResponse:
        return self.web.tell_joke()

    def _quote(self, intent: Intent) -> AssistantResponse:
        return self.web.daily_quote()

    def _meditation(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _workout(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _diet(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _recipe(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _pet_care(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _plant_care(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _home_decor(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _fashion(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _makeup(self, intent: Intent) -> AssistantResponse:
        return self.web.lifestyle_tip(intent.name)

    def _api_test(self, intent: Intent) -> AssistantResponse:
        data = self.coding.api_test(str(intent.args.get("target", "")))
        return AssistantResponse("error" not in data, "API test completed.", intent.name, data=data)

    def _explain_code(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.coding.explain_code(str(intent.args.get("target", ""))))

    def _git_status(self, intent: Intent) -> AssistantResponse:
        data = self.coding.git_status(str(intent.args.get("target", ".")))
        return AssistantResponse(bool(data.get("ok")), "Git status checked.", intent.name, data=data)

    def _git_diff(self, intent: Intent) -> AssistantResponse:
        data = self.coding.git_diff_summary(str(intent.args.get("target", ".")))
        return AssistantResponse(bool(data.get("ok")), "Git diff checked.", intent.name, data=data)

    def _json_validator(self, intent: Intent) -> AssistantResponse:
        message = self.coding.validate_json(str(intent.args.get("target", "")))
        return self._message(intent, message)

    def _safe_shell(self, intent: Intent) -> AssistantResponse:
        data = self.coding.shell_suggestion(str(intent.args.get("target", "")))
        return AssistantResponse(True, "Safe shell suggestion ready.", intent.name, data=data)

    def _read_docs(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.coding.read_docs(Path(str(intent.args.get("target", "README.md")))))

    def _write_docs(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.coding.write_docs(str(intent.args.get("target", ""))))

    def _ai_coder(self, intent: Intent) -> AssistantResponse:
        return self._message(intent, self.coding.ai_coder(str(intent.args.get("target", ""))))

    def _write_tests(self, intent: Intent) -> AssistantResponse:
        tests = self.coding.suggest_tests(str(intent.args.get("target", "")))
        return AssistantResponse(True, "Suggested tests ready.", intent.name, data={"tests": tests})

    def _text_to_speech(self, intent: Intent) -> AssistantResponse:
        text = str(intent.args.get("target", "")).strip()
        if not text:
            data = self.voice.voice_profile()
            return AssistantResponse(True, "Voice profile ready.", intent.name, data=data)
        result = self.voice.speak_text(text)
        return AssistantResponse(
            result.ok,
            result.message,
            intent.name,
            data={"provider": result.provider, "command": result.command},
        )

    def _voice_status(self, intent: Intent) -> AssistantResponse:
        audio = self.audio.diagnostics()
        voice = self.voice.runtime_status()
        ok = audio.recorder_available or audio.stt_available or bool(voice["configured_tts"])
        return AssistantResponse(
            ok,
            "Voice diagnostics ready.",
            intent.name,
            data={
                "audio": {
                    "recorder_available": audio.recorder_available,
                    "stt_available": audio.stt_available,
                    "tts_available": audio.tts_available,
                    "missing_dependencies": list(audio.missing_dependencies),
                    "devices": [device.name for device in audio.devices],
                },
                "stt": {"provider": audio.stt_provider, "available": audio.stt_available},
                "tts": voice,
                "recorder_available": audio.recorder_available,
                "stt_available": audio.stt_available,
                "tts_available": audio.tts_available,
                "devices": [device.name for device in audio.devices],
                "missing_dependencies": list(audio.missing_dependencies),
                "voice": voice,
            },
        )

    def _speech_to_text(self, intent: Intent) -> AssistantResponse:
        source = Path(str(intent.args.get("target", ""))).expanduser()
        try:
            result = self.audio.transcribe(source)
        except FileNotFoundError:
            return AssistantResponse(False, f"Audio file does not exist: {source}", intent.name)
        except RuntimeError as error:
            return AssistantResponse(False, str(error), intent.name, data={"provider": "faster-whisper"})
        return AssistantResponse(
            result.ok,
            result.message if not result.ok else result.text or "Transcription completed with no speech detected.",
            intent.name,
            data={"text": result.text, "language": result.language, "segments": list(result.segments)},
        )

    def _linux_command(self, intent: Intent) -> AssistantResponse:
        data = self.coding.run_allowed_command(str(intent.args.get("target", "")))
        return AssistantResponse("error" not in data, "Command evaluated.", intent.name, data=data)

    def _run_code(self, intent: Intent) -> AssistantResponse:
        data = self.coding.run_python(str(intent.args.get("target", "")))
        return AssistantResponse(data["returncode"] == 0, "Python snippet executed.", intent.name, data=data)

    def _capabilities(self, intent: Intent) -> AssistantResponse:
        implemented = implemented_capabilities()
        names = [capability.name for capability in implemented]
        return AssistantResponse(
            True,
            f"Atlas has {len(implemented)} implemented first-pass capabilities registered.",
            intent.name,
            data={
                "registered": len(CAPABILITIES),
                "implemented": len(names),
                "implemented_names": names,
            },
        )

    def _unknown_response(self, intent: Intent) -> AssistantResponse:
        suggestions = _suggest_capabilities(intent.raw_text)
        hint = ", ".join(suggestions[:3]) if suggestions else "what can you do"
        return AssistantResponse(
            False,
            f"Atlas does not understand that command yet. Try: {hint}",
            intent.name,
            RiskLevel.UNSUPPORTED,
            data={"suggestions": suggestions},
        )

    def _message(
        self, intent: Intent, message: str, data: dict[str, Any] | None = None
    ) -> AssistantResponse:
        capability = capability_by_name(intent.name)
        risk = capability.risk if capability else RiskLevel.SAFE
        return AssistantResponse(True, message, intent.name, risk, data or {})


def _suggest_capabilities(raw_text: str) -> list[str]:
    """Return simple capability suggestions for an unknown command."""
    normalized = raw_text.casefold()
    scored: list[tuple[int, Capability]] = []
    for capability in CAPABILITIES:
        haystack = f"{capability.name} {capability.category} {capability.summary}".casefold()
        score = sum(1 for token in normalized.split() if len(token) > 2 and token in haystack)
        if score:
            scored.append((score, capability))
    scored.sort(key=lambda item: (-item[0], item[1].name))
    return [capability.name for _, capability in scored[:5]]
