from groq import AsyncGroq

from config import GROQ_API_KEY, GROQ_MODEL
from prompt_loader import load_prompts

_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


async def ask_groq(transcript: str) -> str:
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set in .env")

    system_prompt, user_prompt_template = load_prompts()
    user_prompt = user_prompt_template.format(transcript=transcript)

    response = await _client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.8,
        max_tokens=60,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return (response.choices[0].message.content or "").strip()
