import os

from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
PERSONA_NAME = os.getenv("PERSONA_NAME", "cohost")

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 2560
MODE = "llm"
INPUT_DEVICE_INDEX = None

MIN_TRANSCRIPT_CHARS = 12
MIN_CONFIDENCE = 0.25
LLM_COOLDOWN_SECONDS = 2.0
