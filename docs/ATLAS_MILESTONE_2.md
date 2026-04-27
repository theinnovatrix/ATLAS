# Atlas Milestone 2

Milestone 2 adds the first Voice I/O pipeline contracts. The goal is to make
voice support visible, testable, and optional before requiring microphone or
speaker hardware.

## Implemented now

- `AudioProcessor` diagnostics for optional recording and transcription
  providers.
- Optional recording through `sounddevice` and `soundfile` when installed.
- Optional Faster-Whisper transcription when installed.
- Voice provider status for free/local defaults and paid upgrade slots.
- Text-to-speech request preparation through the configured female voice
  provider path.
- CLI routes:
  - `python -m atlas.cli "voice status"`
  - `python -m atlas.cli "say hello"`
  - `python -m atlas.cli "transcribe /path/to/audio.wav"`

## Hardware boundary

This cloud environment cannot validate a physical microphone or speaker. Atlas
therefore reports provider availability and returns clear messages when optional
voice dependencies are missing. Real microphone and speaker testing belongs on
the target Linux desktop.

## Next voice work

- Add wake word detection.
- Add streaming TTS playback for Edge TTS and Piper.
- Add end-to-end microphone to transcription tests on a desktop runner.
