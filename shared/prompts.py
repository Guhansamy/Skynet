from pathlib import Path
import yaml

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(name: str) -> str:
    with open(PROMPTS_DIR / f"{name}.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)["system_prompt"].strip()