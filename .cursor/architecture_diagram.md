# NOVA Voice Assistant Architecture

## Current Repository State

The repository currently contains only a placeholder `README.md` and no application code.
The architecture below is the target structure for the planned NOVA implementation.

## Target Module Map

```text
nova/
├── core/
│   ├── app.py                  # Application lifecycle and dependency wiring
│   ├── config.py               # Environment and settings loader
│   ├── intent_parser.py        # Command classification and routing
│   └── orchestrator.py         # Voice/text request execution pipeline
├── modules/
│   ├── audio_processor.py      # Microphone capture and speech-to-text
│   ├── voice_engine.py         # Text-to-speech generation and playback
│   ├── wake_word.py            # Wake word detection
│   ├── system_control.py       # Volume, brightness, power, app launch
│   ├── file_manager.py         # File search, open, rename, delete, organize
│   ├── web_media.py            # Weather, news, stock, search, media helpers
│   ├── browser_automation.py   # Browser automation for permitted workflows
│   ├── coding_assistant.py     # Coding task helpers and local repo operations
│   └── safety.py               # Consent, allowlists, and destructive action guards
├── gui/
│   ├── main_window.py          # PyQt6 main window
│   ├── voice_thread.py         # Non-blocking voice processing thread
│   └── widgets/
│       ├── chat_display.py     # Conversation display
│       ├── status_indicator.py # Listening/thinking/speaking state
│       └── settings_panel.py   # Runtime configuration UI
├── tests/
│   ├── conftest.py
│   ├── test_audio_processor.py
│   ├── test_voice_engine.py
│   ├── test_intent_parser.py
│   ├── test_system_control.py
│   ├── test_web_media.py
│   └── test_gui_integration.py
└── docs/
    ├── API.md
    ├── DEVELOPMENT.md
    └── SECURITY.md
```

## Request Flow

```text
Microphone
  -> wake_word.WakeWordDetector
  -> audio_processor.AudioProcessor.transcribe()
  -> core.intent_parser.IntentParser.parse()
  -> core.orchestrator.Orchestrator.execute()
  -> selected module handler
  -> voice_engine.VoiceEngine.speak()
  -> gui.main_window.NovaMainWindow status/chat updates
```

## Dependency Boundaries

- `core` owns orchestration and should not import GUI widgets directly.
- `modules` expose narrow service classes with typed return values and structured errors.
- `gui` calls `core` through thread-safe adapters and Qt signals.
- External APIs must be wrapped behind module classes so tests can mock network calls.
- Destructive system or web actions should route through `modules.safety`.

## Security and Platform Notes

- Social platforms such as Instagram, Facebook, and YouTube must be accessed through official APIs or user-authorized browser automation where allowed by their terms.
- Credentials and API keys belong in environment variables or a local ignored config file, never source code.
- The detected environment is Ubuntu 24.04, not Parrot OS; Linux system-control behavior must be validated on the final target OS before release.
