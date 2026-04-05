"""
Configuration loader — Sovereign Core edition.

Reads settings from config/settings.json (relative path resolved at runtime).
Falls back to sensible defaults so the assistant works out of the box.

Backends (priority order):
    sovereign : Qwen2.5-32B-AWQ via OpenAI-compatible API @ TatorTot / localhost
    ollama    : on-device Ollama (fallback / offline mode)
"""
import json
from typing import Any

from assistant.utils import paths as _paths


def _normalize(value: Any, default: Any) -> Any:
    """Coerce *value* to match the type of *default*.

    Handles legacy config files where values may have been stored as strings.
    Returns *value* unchanged when coercion is not applicable or fails.
    """
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
    # ── Backend ──────────────────────────────────────────────────────────────
    # "sovereign" → Qwen2.5-32B-AWQ via local OpenAI-compatible endpoint
    # "ollama"    → on-device Ollama (low RAM, offline)
    "backend": "sovereign",

    # ── Sovereign Core (primary) ─────────────────────────────────────────────
    # Point at TatorTot over LAN:  http://192.168.x.x:8001
    # Or localhost when running on the same machine:  http://localhost:8001
    "sovereign_url": "http://localhost:8001",
    "sovereign_model": "openai/qwen2.5-32b-awq",

    # ── Ollama (fallback / on-device) ────────────────────────────────────────
    "ollama_url": "http://localhost:11434",
    "ollama_model": "tinyllama",

    # ── Behaviour ────────────────────────────────────────────────────────────
    "max_history": 20,        # messages kept in SQLite rolling window
    "max_tokens": 2048,       # maximum tokens per response (int required by backends)
    "stream": True,           # stream tokens as they arrive
    "auto_run_bash": False,   # auto-execute AI-suggested bash without prompt
    "timeout": 60,            # HTTP request timeout (seconds)
    "log_level": "WARNING",
}

#: Public read-only view of the default settings.
DEFAULTS: dict[str, Any] = _DEFAULTS


def load() -> dict[str, Any]:
    """Load settings, merging with defaults."""
    _paths.ensure_data_dir()
    if _paths.CONFIG_FILE.exists():
        try:
            with _paths.CONFIG_FILE.open() as fh:
                user = json.load(fh)
            merged = {**_DEFAULTS, **user}
            for key, default in _DEFAULTS.items():
                merged[key] = _normalize(merged[key], default)
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_DEFAULTS)


def save(settings: dict[str, Any]) -> None:
    """Persist *settings* to config/settings.json."""
    _paths.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _paths.CONFIG_FILE.open("w") as fh:
        json.dump(settings, fh, indent=2)
