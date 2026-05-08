from filters import should_send_to_llm
from llm_service import ask_groq


async def handle_transcript(transcript: str, event: str, confidence=None) -> None:
    if not should_send_to_llm(transcript, confidence):
        return

    try:
        response = await ask_groq(transcript)
    except Exception as exc:
        print(f"LLM error: {exc}")
        return

    if response:
        print(f"AI CO-HOST: {response}", flush=True)
