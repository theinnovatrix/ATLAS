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

## Optional providers

Atlas works without paid keys for the current milestone. Later upgrades can use:

- `GROQ_API_KEY` for low-cost hosted LLM or Whisper.
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
