# StreamPulse

StreamPulse is a local real-time AI co-host pipeline for livestreaming.

Today, this repo focuses on one practical flow:

1. Capture live microphone audio with PyAudio
2. Stream it directly to Deepgram Flux over WebSocket
3. Receive live `TurnInfo` speech events
4. Filter transcripts before they hit the LLM
5. Send accepted turns to Groq asynchronously
6. Print a short AI co-host response back to the console

The code is intentionally simple and modular so prompt editing, persona switching, and model swapping stay easy.

## Current Pipeline

- [streampulse_flux_mic.py](d:/Python/StreamPulse/streampulse_flux_mic.py): main microphone -> Deepgram Flux loop
- [config.py](d:/Python/StreamPulse/config.py): environment loading and runtime settings
- [filters.py](d:/Python/StreamPulse/filters.py): transcript gating and cooldown logic
- [handoff.py](d:/Python/StreamPulse/handoff.py): async transcript -> LLM handoff
- [llm_service.py](d:/Python/StreamPulse/llm_service.py): Groq async chat call
- [prompt_loader.py](d:/Python/StreamPulse/prompt_loader.py): loads persona prompt files from `prompts/`
- [mic_test.py](d:/Python/StreamPulse/mic_test.py): quick input-device testing helper

## Requirements

- Python 3.10+
- A working microphone
- A Deepgram API key
- A Groq API key

## Setup

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements-mic.txt
```

Or use the included helper:

```powershell
.\start.ps1
```

## Environment Variables

Create a `.env` file in the project root with:

```env
DEEPGRAM_API_KEY=your_deepgram_key
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
PERSONA_NAME=cohost
```

Notes:

- `GROQ_MODEL` is optional because [config.py](d:/Python/StreamPulse/config.py) has a default.
- `PERSONA_NAME` selects which prompt pair is loaded from `prompts/`.
- Do not commit `.env`.

## Running

From PowerShell:

```powershell
.\start.ps1
python .\streampulse_flux_mic.py
```

Or directly if the venv is already active:

```powershell
python .\streampulse_flux_mic.py
```

If you need help finding the correct microphone input:

```powershell
python .\mic_test.py
```

## VS Code

This repo includes:

- [.vscode/settings.json](d:/Python/StreamPulse/.vscode/settings.json): points VS Code to `.venv`
- [.vscode/launch.json](d:/Python/StreamPulse/.vscode/launch.json): adds `Run StreamPulse Mic`

To run in VS Code:

1. Open the `D:\Python\StreamPulse` folder
2. Go to `Run and Debug`
3. Select `Run StreamPulse Mic`
4. Press `F5`

## Modes

`MODE` is currently defined in [config.py](d:/Python/StreamPulse/config.py).

- `fast`: prints live transcript deltas only
- `llm`: sends `EagerEndOfTurn` transcripts to the LLM
- `final`: sends `EndOfTurn` transcripts to the LLM

`fast` mode is for live caption-style output and does not send `Update` events to Groq.

## Personas And Prompts

Prompt text lives in the [prompts](d:/Python/StreamPulse/prompts) folder as plain `.txt` files.

Each persona uses two files:

- `<persona>_system.txt`
- `<persona>_user.txt`

Examples currently in the repo:

- `cohost`
- `hype`
- `comedy_writer`

If `.env` contains:

```env
PERSONA_NAME=hype
```

the app loads:

- `prompts/hype_system.txt`
- `prompts/hype_user.txt`

The user prompt should keep the `{transcript}` placeholder so live speech can be inserted automatically.

See [prompts/README.md](d:/Python/StreamPulse/prompts/README.md) for the naming convention.

## Changing The Groq Model

The easiest way to switch models is in `.env`:

```env
GROQ_MODEL=llama-3.3-70b-versatile
```

The model value is read in [config.py](d:/Python/StreamPulse/config.py) and passed into the Groq client call in [llm_service.py](d:/Python/StreamPulse/llm_service.py).

## Filtering Behavior

Before a transcript is sent to Groq, [filters.py](d:/Python/StreamPulse/filters.py) currently rejects:

- empty transcripts
- transcripts shorter than `MIN_TRANSCRIPT_CHARS`
- low-confidence transcripts when confidence is present
- duplicate transcripts
- transcripts that arrive during the cooldown window

These thresholds live in [config.py](d:/Python/StreamPulse/config.py).

## Notes

- The Deepgram connection uses `extra_headers`, which is correct for `websockets==10.3`.
- Groq calls run in background tasks so the Deepgram receive loop stays responsive.
- This repo currently uses a direct WebSocket approach and does not include Redis or a separate queue layer.
