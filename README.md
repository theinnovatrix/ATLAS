# Atlas

Atlas is a local-first Linux desktop voice assistant foundation. It starts with a
safe command router, bilingual English and Hindi/Urdu intent handling, free or
offline default providers, and upgrade hooks for paid AI and voice services.

## Current milestone

- Text command CLI: `python -m atlas.cli "system info"`
- Capability registry for the requested system, desktop, productivity, coding,
  web, and media feature set.
- Safety policy for destructive or privileged operations.
- Free-first providers by default: local rules for intent parsing, `pyttsx3` or
  Piper for TTS, Faster-Whisper for offline speech-to-text, and optional Groq,
  OpenAI, ElevenLabs, Azure, or Google provider slots for later upgrades.
- Voice I/O diagnostics and optional adapters for audio recording, file
  transcription, and text-to-speech provider selection.

## Full step-by-step setup

These steps are for Ubuntu, Debian, or Parrot OS.

### Step 1: Download the project ZIP

1. Open the Atlas GitHub repository in your browser.
2. Click `Code`.
3. Click `Download ZIP`.
4. Save the ZIP file to your `Downloads` folder.

If you prefer Git, you can clone instead:

```bash
git clone https://github.com/theinnovatrix/ATLAS.git
```

### Step 2: Extract the ZIP

If you downloaded the ZIP, extract it with your file manager or run:

```bash
cd ~/Downloads
unzip ATLAS-main.zip
cd ATLAS-main
```

If the folder has a different name, `cd` into that extracted folder instead.

If you cloned with Git, run:

```bash
cd ATLAS
```

### Step 3: Install Linux setup tools

Run:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

If your system uses Python 3.12 and `python3-venv` is not enough, run:

```bash
sudo apt-get install -y python3.12-venv
```

### Step 4: Create a virtual environment

```bash
python3 -m venv .venv
```

### Step 5: Activate the virtual environment

Run this every time you open a new terminal for Atlas:

```bash
source .venv/bin/activate
```

Your terminal should now show `(.venv)` near the prompt.

### Step 6: Install Atlas

Install Atlas in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

### Step 7: Run Atlas for the first time

Run:

```bash
python -m atlas.cli "system info"
```

You should see a system summary from Atlas.

### Step 8: Try basic commands

```bash
python -m atlas.cli "what can you do"
python -m atlas.cli "system info"
python -m atlas.cli "Delhi ka mausam batao"
python -m atlas.cli "calculate 12 * 8"
python -m atlas.cli "translate hello"
python -m atlas.cli "voice status"
python -m atlas.cli "say hello Atlas"
python -m atlas.cli "volume 30"
```

Commands that can change the system require confirmation. For example:

```bash
python -m atlas.cli "volume 30" --confirm
```

After `python -m pip install -e .`, this shortcut also works:

```bash
atlas "what can you do"
```

Atlas is currently a text-command foundation. Full microphone listening, GUI,
screen recording, and deeper desktop automation are planned follow-up milestones.
Voice diagnostics are available now; real microphone recording and speech
playback require optional Linux audio tools and Python packages.

## Developer test setup

Use this if you want to run the automated checks:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Updating an existing laptop install to Milestone 2

Use this section if you already installed Milestone 1 and want the new Voice I/O
milestone.

### Step 1: Open your existing Atlas folder

If you installed from ZIP, go to the extracted folder:

```bash
cd ~/Downloads/ATLAS-main
```

If you installed with Git, go to the cloned folder:

```bash
cd ~/ATLAS
```

Use the actual folder path if you saved Atlas somewhere else.

### Step 2: Get the latest code

If you use Git:

```bash
git pull origin main
```

If you use ZIP:

1. Download the newest ZIP from GitHub.
2. Extract it.
3. Replace your old Atlas folder with the new extracted folder.
4. Open a terminal inside the new folder.

### Step 3: Activate your virtual environment

```bash
source .venv/bin/activate
```

If `.venv` does not exist anymore, recreate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4: Reinstall Atlas and dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

### Step 5: Run the Milestone 1 tests

```bash
python -m pytest tests/test_orchestrator.py -q
```

If only `test_hindi_weather_command_uses_city_argument` failed before, update to
the latest code and rerun it. Atlas now keeps `response.data["city"]` available
even if the free weather endpoint is down.

### Step 6: Run the Milestone 2 tests

```bash
python -m pytest tests/test_voice_io.py -q
```

### Step 7: Try the Milestone 2 commands

```bash
python -m atlas.cli "voice status"
python -m atlas.cli "say hello Atlas"
python -m atlas.cli "transcribe /path/to/audio.wav"
```

`voice status` works without a microphone. Real recording and playback need the
optional audio packages and Linux audio tools listed in `docs/ATLAS_MILESTONE_2.md`.

## Updating an existing laptop install to Milestone 3

Use this after Milestone 2 is working.

### Step 1: Get the latest code

Git install:

```bash
cd ~/ATLAS
git fetch origin
git checkout Atlasnova-agent-planning-0f22
git pull origin Atlasnova-agent-planning-0f22
```

Use `git pull origin main` only after the Milestone 3 PR has been merged into
`main`. Until then, Milestone 3 files such as `tests/test_milestone_3_routing.py`
exist on the active PR branch above.

ZIP install:

1. Download the newest ZIP.
2. Extract it.
3. Replace the old Atlas folder.
4. Open a terminal inside the new folder.

### Step 2: Reinstall and run routing tests

```bash
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_intent_parser.py tests/test_orchestrator.py tests/test_milestone_3_routing.py -q
```

Run each command separately. `python -m pip install -e .` needs the final `.`;
that dot means "install this Atlas folder".

### Step 3: Try Milestone 3 command routing

```bash
python -m atlas.cli "timer 10"
python -m atlas.cli "define atlas"
python -m atlas.cli "todo buy milk"
python -m atlas.cli "open firefox"
python -m atlas.cli "open firefox" --confirm
python -m atlas.cli "make the moon blue" --json
```

Milestone 3 improves intent parsing, slot extraction, unknown-command
suggestions, and confirmation metadata. See `docs/ATLAS_MILESTONE_3.md`.

## Updating an existing laptop install to Milestone 4

Use this after Milestone 3 is working.

### Step 1: Get the latest Milestone 4 branch

```bash
cd ~/ATLAS
git fetch origin
git checkout Atlasmilestone-4-system-control-0f22
git pull origin Atlasmilestone-4-system-control-0f22
```

Use `git pull origin main` only after the Milestone 4 PR has been merged into
`main`.

### Step 2: Reinstall and run system-control tests

```bash
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_system_control.py -q
```

### Step 3: Try Milestone 4 system commands

```bash
python -m atlas.cli "system diagnostics" --json
python -m atlas.cli "notify Atlas hello"
python -m atlas.cli "screenshot" --json
python -m atlas.cli "lock screen" --json
python -m atlas.cli "service ssh status" --json
```

Milestone 4 prepares and validates Linux system commands. Commands that change
your system still require `--confirm`. See `docs/ATLAS_MILESTONE_4.md`.

## Updating an existing laptop install to Milestone 5

Use this after Milestone 4 is working.

### Step 1: Get the latest Milestone 5 branch

```bash
cd ~/ATLAS
git fetch origin
git checkout Atlasmilestone-5-web-integrations-0f22
git pull origin Atlasmilestone-5-web-integrations-0f22
```

Use `git pull origin main` only after the Milestone 5 PR has been merged into
`main`.

### Step 2: Reinstall and run web tests

```bash
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_web_integrations.py -q
```

### Step 3: Try Milestone 5 web commands

```bash
python -m atlas.cli "weather Delhi"
python -m atlas.cli "news technology" --json
python -m atlas.cli "youtube atlas assistant" --json
python -m atlas.cli "summarize https://example.com" --json
python -m atlas.cli "stock AAPL" --json
```

Milestone 5 uses public/free defaults and official API upgrade slots. It does
not bypass login walls, private backends, or social-platform controls. See
`docs/ATLAS_MILESTONE_5.md`.

## Updating an existing laptop install to Milestone 6

Use this after Milestone 5 is working.

### Step 1: Get the latest Milestone 6 branch

```bash
cd ~/ATLAS
git fetch origin
git checkout Atlasmilestone-6-productivity-coding-0f22
git pull origin Atlasmilestone-6-productivity-coding-0f22
```

Use `git pull origin main` only after the Milestone 6 PR has been merged into
`main`.

### Step 2: Reinstall and run productivity/coding tests

```bash
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_productivity_coding.py -q
```

### Step 3: Try Milestone 6 local commands

```bash
python -m atlas.cli "make folder /tmp/atlas-demo"
python -m atlas.cli "note remember to test milestone six"
python -m atlas.cli "copy path README.md"
python -m atlas.cli "git status" --json
python -m atlas.cli "suggest shell list files" --json
```

Milestone 6 focuses on local productivity and coding helpers. Destructive file
operations are still blocked or confirmation-gated. See `docs/ATLAS_MILESTONE_6.md`.

## Updating an existing laptop install to Milestone 8

Use this after Milestone 6 is working. Milestone 8 adds the free-first AI brain
that understands more natural commands before falling back to exact rules.

### Step 1: Get the latest Milestone 8 branch

```bash
cd ~/ATLAS
git fetch origin
git checkout Atlasmilestone-8-ai-brain-0f22
git pull origin Atlasmilestone-8-ai-brain-0f22
```

Use `git pull origin main` only after the Milestone 8 PR has been merged into
`main`.

### Step 2: Reinstall and run AI brain tests

```bash
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_ai_brain.py tests/test_config_and_safety.py -q
```

### Step 3: Add optional free/low-cost API keys

Atlas works without keys through local deterministic planning. If you want hosted
free-tier planning later, set either or both:

```bash
export GEMINI_API_KEY="your_gemini_key_here"
export GROQ_API_KEY="your_groq_key_here"
```

### Step 4: Try flexible AI-brain commands

```bash
python -m atlas.cli "please lower the sound a little" --json
python -m atlas.cli "find news about linux today" --json
python -m atlas.cli "please define atlas for me" --json
python -m atlas.cli "start a focus session for 15 minutes" --json
```

Milestone 8 keeps a free-first setup: local deterministic planner first, Gemini
and Groq free-tier slots next, paid providers later. Voice defaults remain
bilingual and female-oriented through Edge TTS/Piper plus optional ElevenLabs.
See `docs/ATLAS_MILESTONE_8.md`.

## Updating an existing laptop install to Milestone 9

Use this after Milestone 8 is working. Milestone 9 lets Atlas call Gemini or
Groq only when local planning cannot understand a command.

### Step 1: Get the latest Milestone 9 branch

```bash
cd ~/ATLAS
git fetch origin
git checkout Atlasmilestone-9-hosted-ai-0f22
git pull origin Atlasmilestone-9-hosted-ai-0f22
```

### Step 2: Reinstall and run hosted-AI tests

```bash
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_ai_brain.py -q
```

### Step 3: Add free-tier keys

```bash
export GEMINI_API_KEY="your_gemini_key_here"
export GROQ_API_KEY="your_groq_key_here"
```

### Step 4: Try hosted fallback

```bash
python -m atlas.cli "please organize my desktop files" --json
python -m atlas.cli "please find online linux voice assistant" --json
```

Atlas still validates hosted AI output against known safe Atlas intents. It will
not run invented tools or dangerous actions. See `docs/ATLAS_MILESTONE_9.md`.

## Optional providers

Atlas works without paid keys for the current milestone. Later upgrades can use:

- `GROQ_API_KEY` for low-cost hosted LLM or Whisper.
- `GEMINI_API_KEY` for Gemini free-tier AI planning.
- `OPENROUTER_API_KEY` for free/low-cost model routing.
- `ELEVENLABS_API_KEY` for premium female TTS voices.
- `SERPAPI_API_KEY` for structured web search.

Set keys only in your shell or a local ignored environment file, never in source
code.

Example:

```bash
export GROQ_API_KEY="your_key_here"
export OPENROUTER_API_KEY="your_key_here"
export ELEVENLABS_API_KEY="your_key_here"
export SERPAPI_API_KEY="your_key_here"
```

## Troubleshooting

### `python3 -m venv .venv` fails

Install venv support:

```bash
sudo apt-get install -y python3-venv
```

For Python 3.12:

```bash
sudo apt-get install -y python3.12-venv
```

### `ModuleNotFoundError: No module named 'atlas'`

Activate the virtual environment and reinstall Atlas:

```bash
source .venv/bin/activate
python -m pip install -e .
```

### `pytest` is not found

Install developer tools:

```bash
python -m pip install -r requirements-dev.txt
```

### System commands ask for confirmation

That is expected. Atlas blocks risky actions unless you add `--confirm`.
