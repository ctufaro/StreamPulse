import time

from config import LLM_COOLDOWN_SECONDS, MIN_CONFIDENCE, MIN_TRANSCRIPT_CHARS

_last_transcript = ""
_last_sent_at = 0.0


def should_send_to_llm(transcript: str, confidence=None) -> bool:
    global _last_transcript, _last_sent_at

    cleaned = (transcript or "").strip()
    if not cleaned:
        return False

    if len(cleaned) < MIN_TRANSCRIPT_CHARS:
        return False

    if confidence is not None and confidence < MIN_CONFIDENCE:
        return False

    if cleaned == _last_transcript:
        return False

    now = time.monotonic()
    if now - _last_sent_at < LLM_COOLDOWN_SECONDS:
        return False

    _last_transcript = cleaned
    _last_sent_at = now
    return True
