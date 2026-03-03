"""
Configuration loader.

Reads settings from config/settings.json (relative path resolved at runtime).
Falls back to sensible defaults so the assistant works out of the box.
"""
import json
from typing import Any

from assistant.utils.paths import CONFIG_FILE, ensure_data_dir


def _normalize(value: Any, default: Any) -> Any:
    """Coerce *value* to match the type of *default*.

    Handles legacy config files where values may have been stored as strings.
    Returns *value* unchanged when coercion is not applicable or fails.
    """
    # bool must be checked before int (bool is a subclass of int)
    if isinstance(default, bool):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.strip().lower() in ("true", "1", "yes"):
                return True
            if value.strip().lower() in ("false", "0", "no"):
                return False
        if isinstance(value, int):
            return bool(value)
        return value
    if isinstance(default, int) and not isinstance(value, int):
        try:
            return int(value)
        except (ValueError, TypeError):
            return value
    if isinstance(default, float) and not isinstance(value, (int, float)):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value
    return value

_DEFAULTS: dict[str, Any] = {
    # Backend: "ollama" (local LLM), "openai", "anthropic", "mistral", or "llama" (via Groq)
    "backend": "ollama",
    "ollama_model": "tinyllama",      # tiny model — low RAM footprint
    "ollama_url": "http://localhost:11434",
    "openai_model": "gpt-4o-mini",
    "openai_api_key": "",
    "anthropic_model": "claude-3-5-sonnet-20241022",
    "anthropic_api_key": "",
    "anthropic_max_tokens": 4096,
    "mistral_model": "mistral-small-latest",
    "mistral_api_key": "",
    "groq_model": "llama-3.3-70b-versatile",
    "groq_api_key": "",
    # Memory limits — keep footprint small on mobile
    "max_history": 20,
    "stream": True,
    "log_level": "WARNING",
}

#: Public read-only view of the default settings.
DEFAULTS: dict[str, Any] = _DEFAULTS


def load() -> dict[str, Any]:
    """Load settings, merging with defaults."""
    ensure_data_dir()
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open() as fh:
                user = json.load(fh)
            merged = {**_DEFAULTS, **user}
            # Normalize types to fix values stored with wrong types (e.g. strings)
            for key, default in _DEFAULTS.items():
                merged[key] = _normalize(merged[key], default)
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_DEFAULTS)


def save(settings: dict[str, Any]) -> None:
    """Persist *settings* to config/settings.json."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as fh:
        json.dump(settings, fh, indent=2)
