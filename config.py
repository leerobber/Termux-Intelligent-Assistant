"""Configuration loader for Termux Intelligent Assistant."""

import os

# Try to load config.env if it exists
_config_path = os.path.join(os.path.dirname(__file__), "config.env")
if os.path.isfile(_config_path):
    with open(_config_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _value = _line.partition("=")
                os.environ.setdefault(_key.strip(), _value.strip())

AI_PROVIDER: str = os.environ.get("AI_PROVIDER", "openai").lower()
AI_MODEL: str = os.environ.get("AI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")

MAX_TOKENS: int = int(os.environ.get("MAX_TOKENS", "2048"))

SYSTEM_PROMPT: str = (
    "You are an intelligent assistant embedded in a Termux terminal on Android. "
    "You help users learn, troubleshoot, and automate anything related to Termux, "
    "Linux command-line tools, shell scripting, package management, and programming. "
    "When providing commands, format them as code blocks. "
    "Be concise, practical, and beginner-friendly."
)
