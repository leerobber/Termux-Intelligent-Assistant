"""
Configuration loader.

Reads settings from config/settings.json (relative path resolved at runtime).
Falls back to sensible defaults so the assistant works out of the box.
"""
import json
from typing import Any

from assistant.utils.paths import CONFIG_FILE, ensure_data_dir

_DEFAULTS: dict[str, Any] = {
    # Backend: "ollama" (local LLM), "openai", "anthropic", "mistral", or "llama" (via Groq)
    "backend": "ollama",
    "ollama_model": "tinyllama",      # tiny model — low RAM footprint
    "ollama_url": "http://localhost:11434",
    "openai_model": "gpt-4o-mini",
    "openai_api_key": "",
    "anthropic_model": "claude-3-5-sonnet-20241022",
    "anthropic_api_key": "",
    "mistral_model": "mistral-small-latest",
    "mistral_api_key": "",
    "groq_model": "llama-3.3-70b-versatile",
    "groq_api_key": "",
    # Memory limits — keep footprint small on mobile
    "max_history": 20,
    "stream": True,
    "log_level": "WARNING",
}


def load() -> dict[str, Any]:
    """Load settings, merging with defaults."""
    ensure_data_dir()
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open() as fh:
                user = json.load(fh)
            return {**_DEFAULTS, **user}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_DEFAULTS)


def save(settings: dict[str, Any]) -> None:
    """Persist *settings* to config/settings.json."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as fh:
        json.dump(settings, fh, indent=2)
