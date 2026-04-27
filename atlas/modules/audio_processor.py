"""
Module: atlas.modules.audio_processor
Purpose: Optional audio recording and transcription adapters for Atlas.
Author: NOVA Development Agent
Version: 0.2.0
Dependencies: standard library, optional sounddevice, optional faster_whisper
Last Updated: 2026-04-27
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol
import importlib.util
import wave


@dataclass(frozen=True)
class AudioDevice:
    """Audio input or output device detected by Atlas."""

    name: str
    input_channels: int = 0
    output_channels: int = 0
    sample_rate: int = 16000


@dataclass(frozen=True)
class AudioDiagnostics:
    """Voice I/O dependency and device status."""

    recorder_available: bool
    stt_available: bool
    tts_available: bool
    devices: tuple[AudioDevice, ...] = ()
    missing_dependencies: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @property
    def stt_provider(self) -> str:
        """Return the preferred speech-to-text provider."""
        return "faster-whisper"

    @property
    def recorder_provider(self) -> str:
        """Return the active recorder provider name."""
        return "sounddevice" if self.recorder_available else "unavailable"

    @property
    def ready_for_transcription(self) -> bool:
        """Return whether transcription can run right now."""
        return self.stt_available


@dataclass(frozen=True)
class RecordingResult:
    """Saved audio recording metadata."""

    path: Path
    duration_seconds: float
    sample_rate: int
    channels: int


@dataclass(frozen=True)
class TranscriptionResult:
    """Speech-to-text result."""

    text: str
    language: str = "unknown"
    segments: tuple[str, ...] = field(default_factory=tuple)
    ok: bool = True
    provider: str = "faster-whisper"
    message: str = "Transcription complete."


class AudioInputBackend(Protocol):
    """Recording backend interface used by Atlas."""

    def list_devices(self) -> tuple[AudioDevice, ...]:
        """Return detected devices."""

    def record_wav(self, path: Path, duration_seconds: float, sample_rate: int) -> RecordingResult:
        """Record audio to a wav file."""


class SoundDeviceBackend:
    """Audio backend using optional `sounddevice` and `soundfile` packages."""

    def __init__(self) -> None:
        """Import optional sound packages only when this backend is used."""
        try:
            import sounddevice as sounddevice_module  # type: ignore[import-not-found]
            import soundfile as soundfile_module  # type: ignore[import-not-found]
        except ImportError as error:
            raise RuntimeError("Install Atlas voice extras to record audio.") from error
        self._sounddevice = sounddevice_module
        self._soundfile = soundfile_module

    def list_devices(self) -> tuple[AudioDevice, ...]:
        """Return sounddevice devices."""
        devices: list[AudioDevice] = []
        for item in self._sounddevice.query_devices():
            devices.append(
                AudioDevice(
                    name=str(item.get("name", "unknown")),
                    input_channels=int(item.get("max_input_channels", 0)),
                    output_channels=int(item.get("max_output_channels", 0)),
                    sample_rate=int(item.get("default_samplerate", 16000)),
                )
            )
        return tuple(devices)

    def record_wav(self, path: Path, duration_seconds: float, sample_rate: int) -> RecordingResult:
        """Record mono audio to a wav file."""
        frames = int(duration_seconds * sample_rate)
        data = self._sounddevice.rec(frames, samplerate=sample_rate, channels=1, dtype="float32")
        self._sounddevice.wait()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._soundfile.write(str(path), data, sample_rate)
        return RecordingResult(path=path, duration_seconds=duration_seconds, sample_rate=sample_rate, channels=1)


class SilentWavBackend:
    """Deterministic backend for tests and no-microphone environments."""

    def list_devices(self) -> tuple[AudioDevice, ...]:
        """Return a virtual test microphone."""
        return (AudioDevice(name="Atlas virtual microphone", input_channels=1),)

    def record_wav(self, path: Path, duration_seconds: float, sample_rate: int) -> RecordingResult:
        """Create a silent wav file."""
        frame_count = int(duration_seconds * sample_rate)
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b"\x00\x00" * frame_count)
        return RecordingResult(path=path, duration_seconds=duration_seconds, sample_rate=sample_rate, channels=1)


class AudioProcessor:
    """Coordinate audio diagnostics, recording, and transcription."""

    def __init__(
        self,
        backend: AudioInputBackend | None = None,
        model_factory: Any | None = None,
    ) -> None:
        """Initialize optional backend dependencies."""
        self.backend = backend
        self.model_factory = model_factory

    def diagnostics(self) -> AudioDiagnostics:
        """Return current voice dependency and device status without failing."""
        missing = []
        notes = []
        if importlib.util.find_spec("sounddevice") is None:
            missing.append("sounddevice")
        if importlib.util.find_spec("soundfile") is None:
            missing.append("soundfile")
        if importlib.util.find_spec("faster_whisper") is None:
            missing.append("faster-whisper")
        if importlib.util.find_spec("edge_tts") is None:
            notes.append("edge-tts not installed; free neural TTS playback is unavailable.")

        devices: tuple[AudioDevice, ...] = ()
        if self.backend is not None:
            devices = self.backend.list_devices()
        elif "sounddevice" not in missing and "soundfile" not in missing:
            try:
                devices = SoundDeviceBackend().list_devices()
            except RuntimeError:
                devices = ()

        return AudioDiagnostics(
            recorder_available="sounddevice" not in missing and "soundfile" not in missing,
            stt_available="faster-whisper" not in missing,
            tts_available="edge-tts" not in missing or importlib.util.find_spec("pyttsx3") is not None,
            devices=devices,
            missing_dependencies=tuple(missing),
            notes=tuple(notes),
        )

    def record(self, path: str | Path, duration_seconds: float = 5.0, sample_rate: int = 16000) -> RecordingResult:
        """Record a wav file through the configured backend."""
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        backend = self.backend or SoundDeviceBackend()
        return backend.record_wav(Path(path).expanduser(), duration_seconds, sample_rate)

    def transcribe(self, path: str | Path, model_size: str = "base") -> TranscriptionResult:
        """Transcribe an audio file with Faster-Whisper or an injected fake model."""
        audio_path = Path(path).expanduser()
        if not audio_path.exists():
            return TranscriptionResult(
                text="",
                ok=False,
                message=f"Audio file does not exist: {audio_path}",
            )

        if self.model_factory is None:
            try:
                from faster_whisper import WhisperModel  # type: ignore[import-not-found]
            except ImportError as error:
                return TranscriptionResult(
                    text="",
                    ok=False,
                    message=f"Install faster-whisper to transcribe audio: {error}",
                )
            model = WhisperModel(model_size)
        else:
            model = self.model_factory(model_size)

        segments, info = model.transcribe(str(audio_path))
        texts = tuple(str(segment.text).strip() for segment in segments if str(segment.text).strip())
        language = str(getattr(info, "language", "unknown"))
        return TranscriptionResult(text=" ".join(texts).strip(), language=language, segments=texts)

    def transcribe_file(self, path: str | Path, model_size: str = "base") -> TranscriptionResult:
        """Compatibility wrapper for transcribing a file path."""
        return self.transcribe(path, model_size)
