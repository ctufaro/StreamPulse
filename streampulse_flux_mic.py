import asyncio
import json
from urllib.parse import urlencode

import pyaudio
import websockets

from config import (
    CHANNELS,
    CHUNK_SIZE,
    DEEPGRAM_API_KEY,
    INPUT_DEVICE_INDEX,
    MODE,
    SAMPLE_RATE,
)
from handoff import handle_transcript


def open_mic():
    audio = pyaudio.PyAudio()

    print("\nInput devices:")
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            print(f"{i}: {info['name']}")

    if INPUT_DEVICE_INDEX is None:
        print("\nOpening default mic...\n")
    else:
        print(f"\nOpening input device {INPUT_DEVICE_INDEX}...\n")

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=INPUT_DEVICE_INDEX,
        frames_per_buffer=CHUNK_SIZE,
    )

    return audio, stream


async def send_audio(ws, stream):
    print("Listening... talk now.\n")

    try:
        while True:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            await ws.send(data)

            # PyAudio read already blocks naturally.
            # This yields control back to the event loop.
            await asyncio.sleep(0)

    except asyncio.CancelledError:
        pass


async def receive_messages(ws):
    last_fast_transcript = ""

    async for raw_message in ws:
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError:
            print("Non-JSON message:", raw_message)
            continue

        msg_type = message.get("type")
        event = message.get("event")
        transcript = (message.get("transcript") or "").strip()
        confidence = message.get("end_of_turn_confidence")

        if msg_type == "Connected":
            print("Connected to Deepgram Flux.")
            continue

        if msg_type == "Error":
            print("Deepgram error:")
            print(json.dumps(message, indent=2))
            continue

        if msg_type != "TurnInfo":
            continue

        # ------------------------
        # MODE 1: FAST
        # ------------------------
        # Fastest possible output.
        # Uses Update events while you're still speaking.
        # Best for live captions or keeping latest transcript in memory.
        if MODE == "fast":
            if event == "Update" and transcript:
                # Print only the newly-added portion when possible
                if transcript.startswith(last_fast_transcript):
                    delta = transcript[len(last_fast_transcript):].strip()
                else:
                    delta = transcript

                if delta:
                    print(delta, end=" ", flush=True)

                last_fast_transcript = transcript

            elif event == "EndOfTurn":
                print()
                last_fast_transcript = ""

            continue

        # ------------------------
        # MODE 2: LLM
        # ------------------------
        # Best for your AI co-host.
        # Faster than EndOfTurn, less noisy than Update.
        if MODE == "llm":
            if event == "EagerEndOfTurn" and transcript:
                print(f"[LLM/EagerEndOfTurn] {transcript}  confidence={confidence}", flush=True)
                asyncio.create_task(handle_transcript(transcript, event, confidence))

            # Optional: if you later do speculative LLM work,
            # TurnResumed means "Chris kept talking, cancel the draft."
            elif event == "TurnResumed":
                print("[TurnResumed] Ignore previous draft.", flush=True)

            continue

        # ------------------------
        # MODE 3: FINAL
        # ------------------------
        # Cleanest option.
        # Slower, but most stable.
        if MODE == "final":
            if event == "EndOfTurn" and transcript:
                print(f"[FINAL/EndOfTurn] {transcript}  confidence={confidence}", flush=True)
                asyncio.create_task(handle_transcript(transcript, event, confidence))

            continue


async def main():
    if not DEEPGRAM_API_KEY:
        raise RuntimeError("DEEPGRAM_API_KEY is not set in .env")

    if MODE not in {"fast", "llm", "final"}:
        raise RuntimeError('MODE must be one of: "fast", "llm", "final"')

    params = {
        "model": "flux-general-en",
        "encoding": "linear16",
        "sample_rate": str(SAMPLE_RATE),

        # Lower = faster but more false starts.
        # Deepgram valid range: 0.3 - 0.9
        "eager_eot_threshold": "0.3",

        # EndOfTurn confidence threshold.
        "eot_threshold": "0.7",

        # Silence timeout before forcing EndOfTurn.
        # Lower = faster endings, but can cut you off if you pause.
        "eot_timeout_ms": "1000",
    }

    url = f"wss://api.deepgram.com/v2/listen?{urlencode(params)}"

    audio, stream = open_mic()

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
    }

    print(f"Connecting directly to Deepgram Flux...")
    print(f"Mode: {MODE}")

    try:
        async with websockets.connect(
            url,
            extra_headers=headers,
            ping_interval=20,
            ping_timeout=20,
            max_size=None,
        ) as ws:
            print("WebSocket connected.")

            sender = asyncio.create_task(send_audio(ws, stream))
            receiver = asyncio.create_task(receive_messages(ws))

            done, pending = await asyncio.wait(
                [sender, receiver],
                return_when=asyncio.FIRST_EXCEPTION,
            )

            for task in pending:
                task.cancel()

            for task in done:
                exception = task.exception()
                if exception:
                    raise exception

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("\nMic closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
