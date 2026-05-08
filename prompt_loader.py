from pathlib import Path

from config import PERSONA_NAME

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _read_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path.name}")

    return path.read_text(encoding="utf-8").strip()


def load_prompts(persona_name: str | None = None) -> tuple[str, str]:
    persona = persona_name or PERSONA_NAME
    system_path = PROMPTS_DIR / f"{persona}_system.txt"
    user_path = PROMPTS_DIR / f"{persona}_user.txt"
    return _read_prompt(system_path), _read_prompt(user_path)
