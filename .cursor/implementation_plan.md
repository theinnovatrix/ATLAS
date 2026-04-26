# NOVA Voice Assistant Implementation Plan

## Current State

- Repository contains only `README.md`; no Python package structure exists yet.
- No `requirements.txt`, `pyproject.toml`, `setup.py`, application entry point, modules, GUI, tests, or docs are present.
- Python 3.12.3 is available.
- Host OS is Ubuntu 24.04.4 LTS, not Parrot OS.
- Existing installed Python packages include `requests`, `numpy`, and `dbus-python`; core voice, GUI, lint, test, and packaging dependencies are missing.

## Scope Boundaries

NOVA should be implemented as a modular Linux voice assistant. Social and web data integrations must use lawful, documented, authorized APIs or user-provided exports. The implementation should not bypass authentication, scrape private data without permission, defeat platform controls, or automate abusive access to services such as Instagram, Facebook, or YouTube.

## Technical Success Criteria

- Voice command loop: wake/listen, transcribe, parse intent, execute action, respond with TTS.
- Local-first operation where practical, with external providers isolated behind adapters.
- Clear permission model for system control and external API access.
- GUI remains responsive while voice, web, and system tasks execute in worker threads or async tasks.
- Automated tests cover core intent parsing, command routing, system command wrappers, web adapters, configuration, and error handling.
- Quality checks include formatting, linting, type checking, tests, and security scanning.

## Feature Inventory

### Voice and Audio

1. Microphone device discovery.
2. Microphone permission diagnostics.
3. Push-to-talk recording.
4. Wake-word activation.
5. Voice activity detection.
6. Configurable recording duration.
7. Noise-level sampling.
8. Audio normalization.
9. Audio file persistence for debugging.
10. Faster-Whisper transcription.
11. Offline transcription fallback.
12. Transcription confidence reporting.
13. Language auto-detection.
14. Manual language selection.
15. Text-to-speech response generation.
16. Offline TTS fallback.
17. Streaming TTS playback.
18. Voice selection.
19. TTS speed configuration.
20. TTS volume configuration.
21. Conversation interruption handling.
22. Hotword disable switch.
23. Audio device settings panel.
24. Latency measurement.
25. Audio error diagnostics.

### Intent and Conversation

26. Rule-based intent parsing.
27. LLM-backed intent parsing.
28. Command confidence scoring.
29. Confirmation prompts for risky actions.
30. Natural-language slot extraction.
31. Multi-turn context.
32. Chat history persistence.
33. Configurable assistant persona.
34. Task summary generation.
35. Error explanation responses.
36. Help intent.
37. Cancel intent.
38. Repeat last response.
39. Re-run last action.
40. Command alias management.
41. User preference storage.
42. Safe-mode command routing.
43. Structured response objects.
44. Intent audit logging.
45. Unknown-intent fallback.

### Linux System Control

46. Volume get/set.
47. Volume mute/unmute.
48. Brightness get/set.
49. Display sleep command.
50. Wi-Fi status query.
51. Bluetooth status query.
52. Battery status query.
53. CPU usage query.
54. Memory usage query.
55. Disk usage query.
56. Process list query.
57. Application launcher.
58. Application close request.
59. Terminal command execution with allowlist.
60. Screenshot capture.
61. Clipboard read/write with consent.
62. Window list query.
63. Focus application window.
64. Open URL in browser.
65. Open file or folder.
66. System notification send.
67. System lock command.
68. Shutdown with confirmation.
69. Reboot with confirmation.
70. System service status query.

### File and Productivity

71. File search.
72. Directory search.
73. File open.
74. File create.
75. File rename.
76. File move.
77. File copy.
78. File delete with confirmation.
79. Directory create.
80. Recent files query.
81. Note creation.
82. Todo creation.
83. Todo listing.
84. Todo completion.
85. Reminder creation.
86. Calendar event creation via provider API.
87. Timer start.
88. Timer cancel.
89. Stopwatch start/stop.
90. Text summarization for local files.
91. PDF text extraction.
92. CSV summary.
93. JSON validation.
94. Markdown preview support.
95. Export conversation transcript.

### Web and External Data

96. Weather lookup.
97. Stock quote lookup.
98. News headline lookup.
99. Web search through an approved API.
100. Web page summarization for public URLs.
101. RSS feed ingestion.
102. YouTube metadata lookup through official APIs.
103. YouTube transcript retrieval where available and permitted.
104. Facebook integration through Graph API where authorized.
105. Instagram integration through Graph API where authorized.
106. OAuth credential storage.
107. API rate-limit handling.
108. API retry logic.
109. API timeout handling.
110. API response validation.
111. API quota diagnostics.
112. User-agent configuration for public requests.
113. Robots and terms compliance notes.
114. Download manager for permitted files.
115. Link preview generation.
116. Bookmark creation.
117. Website status check.
118. DNS lookup helper.
119. Public IP lookup.
120. Speed test integration.

### Coding Assistant

121. Explain selected code.
122. Generate Python snippets.
123. Generate shell commands with risk labels.
124. Run tests on request.
125. Summarize test failures.
126. Format code.
127. Lint code.
128. Search repository files.
129. Create simple project scaffolds.
130. Git status summary.
131. Git diff summary.
132. Commit message suggestion.
133. Dependency vulnerability summary.
134. README generation.
135. API documentation generation.
136. Regex helper.
137. JSON schema helper.
138. SQL query helper.
139. Docker command helper.
140. Python virtualenv helper.

### GUI

141. Main PyQt6 window.
142. Chat transcript panel.
143. Microphone button.
144. Assistant status indicator.
145. Audio level meter.
146. Settings panel.
147. API key configuration UI.
148. Voice settings UI.
149. System permissions diagnostics UI.
150. Command history view.
151. Activity log view.
152. Error banner component.
153. Theme support.
154. Keyboard shortcuts.
155. Tray icon.
156. Background worker thread.
157. Graceful shutdown.
158. Responsive layout.
159. Accessibility labels.
160. GUI integration tests.

### Security, Privacy, and Reliability

161. Environment-variable secret loading.
162. Optional local encrypted config.
163. Redacted logs for secrets.
164. Command allowlist.
165. Risky command confirmation.
166. Network request timeout defaults.
167. Retry with backoff.
168. Circuit breaker for failing APIs.
169. Structured logging.
170. Debug log rotation.
171. Crash reporting to local files.
172. Privacy mode.
173. Disable transcript persistence.
174. Clear local history.
175. Dependency audit.
176. Bandit security scan.
177. Input validation.
178. Output validation.
179. Permission documentation.
180. Safe defaults.

### Packaging and Operations

181. `pyproject.toml`.
182. `requirements.txt`.
183. Optional `requirements-dev.txt`.
184. Console entry point.
185. Desktop entry file.
186. Systemd user service.
187. AppImage packaging plan.
188. Installation script.
189. Uninstall script.
190. Health check command.
191. Configuration template.
192. Example environment file.
193. Developer setup guide.
194. User setup guide.
195. Troubleshooting guide.
196. API documentation.
197. Architecture documentation.
198. Test coverage report.
199. CI workflow proposal.
200. Release checklist.
201. Versioning policy.
202. Changelog.
203. License review.
204. Fresh-machine install verification.

## Implementation Sequence

### Milestone 1: Foundation

- Create `pyproject.toml`, `requirements.txt`, and package directories.
- Add config loading, logging setup, typed result models, and command registry.
- Add pytest, formatting, linting, type checking, and security tooling.
- Build initial tests for config, logging, and command registration.

### Milestone 2: Voice I/O Pipeline

- Implement audio recording abstraction with PyAudio or sounddevice.
- Implement speech-to-text adapter using Faster-Whisper.
- Implement TTS adapter with ElevenLabs and offline fallback.
- Add audio fixtures and mocked tests for device and provider failures.

### Milestone 3: Intent and Command Routing

- Implement intent parser, slot extraction, command dispatcher, and response models.
- Add confirmation flow for destructive or privileged operations.
- Test command parsing, unknown intents, and risky-action gating.

### Milestone 4: Linux System Control

- Implement volume, brightness, app launch, file open, notifications, and diagnostics.
- Use wrappers around subprocess and DBus with strict command allowlists.
- Add mocked integration tests for subprocess and platform-dependent behavior.

### Milestone 5: Web Integrations

- Implement weather, news, search, YouTube metadata, and authorized Meta Graph API adapters.
- Add retry, timeout, response validation, and rate-limit handling.
- Mock external APIs in tests.

### Milestone 6: Productivity and Coding Tools

- Add file operations, notes, todos, timers, repository helpers, and safe shell suggestions.
- Test path validation, confirmation gates, and error handling.

### Milestone 7: GUI

- Build PyQt6 main window, chat panel, microphone control, settings, and activity log.
- Keep long-running actions off the UI thread.
- Add focused GUI tests and perform manual UI walkthrough testing.

### Milestone 8: Packaging and Documentation

- Add service files, desktop entry, packaging scripts, and release checklist.
- Complete README, API docs, development guide, and troubleshooting guide.
- Verify installation instructions in a clean environment where available.

## Critical Path

1. Foundation package, config, logging, and tests.
2. Intent routing contracts and result models.
3. Voice input/transcription and TTS adapters.
4. System control wrappers.
5. Web adapters.
6. GUI integration.
7. Packaging and operational docs.

## API Keys and Credentials Needed

- ElevenLabs API key for premium TTS.
- OpenAI or another LLM provider key if LLM-backed intent parsing is enabled.
- Weather provider key if replacing `wttr.in` with a production service.
- News API key for news aggregation.
- Stock market data provider key.
- Google API key for YouTube Data API.
- Meta app credentials and OAuth flow for Instagram/Facebook Graph API access.

## System Packages Needed

- `python3-dev`
- `python3-venv`
- `build-essential`
- `portaudio19-dev`
- `alsa-utils`
- `pulseaudio-utils` or PipeWire equivalents
- `ffmpeg`
- `espeak-ng` or Piper runtime dependencies for offline TTS
- `libdbus-1-dev`
- `qt6-base-dev` or PyQt6 runtime libraries
- `xclip` or `wl-clipboard`
- `brightnessctl`
- `libnotify-bin`

## Approximate Code Size by Area

- Foundation and config: 800-1,200 lines.
- Voice I/O: 1,200-1,800 lines.
- Intent routing: 1,000-1,500 lines.
- System control: 1,000-1,600 lines.
- Web integrations: 1,500-2,500 lines.
- Productivity and coding tools: 1,500-2,500 lines.
- GUI: 2,000-3,500 lines.
- Tests: 4,000-7,000 lines.
- Documentation and packaging: 1,500-3,000 lines.

## Blockers and Risks

- Host OS is Ubuntu, so Parrot OS-specific validation cannot be completed in this environment.
- No project code exists yet, so all architecture and dependencies are greenfield.
- Voice hardware, desktop session, DBus, audio server, and GUI availability require runtime validation on the target machine.
- Instagram, Facebook, and YouTube integrations require official API access, OAuth scopes, and compliance with platform terms.
- API keys and secrets must be supplied through environment variables or a secure local config, never committed.

## First Implementation Tasks After Approval

1. Create package structure: `nova/`, `nova/core/`, `nova/modules/`, `nova/gui/`, `tests/`, and `docs/`.
2. Add `pyproject.toml` with runtime and development dependencies.
3. Implement logging and config modules with tests.
4. Implement command result models and command registry with tests.
5. Add README setup instructions and initial development guide.
