"""
assistant/core/agent.py — Intelligent Agent (Sovereign Core edition)
====================================================================
Backend priority:
  1. Sovereign Core Gateway  — full cluster routing (RTX 5050 → Radeon 780M → Ryzen 7)
  2. Direct Ollama (LAN)     — if gateway unreachable, try ollama directly
  3. CPU Ryzen fallback       — direct REST on :8003

Zero third-party deps — pure Python stdlib (urllib, json, sqlite3).
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Iterator

from assistant.core.config import DEFAULTS, load as load_config
from assistant.core.memory import Memory
from assistant.core.sovereign_client import infer, status as sovereign_status
from assistant.tools.system_info import get_context

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an intelligent assistant specialized in Termux and mobile Linux environments. "
    "Give concise, accurate answers. When suggesting shell commands, wrap them in "
    "```bash ... ``` fences. If asked about Sovereign Core status, use the tools available.\n\n"
    "System context:\n{context}"
)


class Agent:
    """
    Stateful conversational agent with Sovereign Core routing.
    
    Maintains conversation history in SQLite, builds full message context
    on each turn, and routes through the Sovereign Core gateway with
    automatic fallback to direct Ollama backends.
    """

    def __init__(self) -> None:
        self._cfg = load_config()
        self._memory = Memory(max_history=self._cfg.get("max_history", 20))
        self._system = _SYSTEM_PROMPT.format(context=get_context())
        self._request_count = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def chat(self, user_input: str) -> str:
        """Send user_input, get response, store both in memory."""
        self._memory.add("user", user_input)
        self._request_count += 1

        try:
            reply = self._route(user_input)
        except Exception as exc:
            reply = f"[Error] {exc}\n\nTry: python -m assistant.main status"
            logger.error("Chat error: %s", exc)

        self._memory.add("assistant", reply)
        return reply

    def status(self) -> dict:
        """Return current backend connectivity status."""
        return sovereign_status()

    def reset(self) -> None:
        """Clear conversation history."""
        self._memory.clear()

    @property
    def request_count(self) -> int:
        return self._request_count

    # ── Routing ───────────────────────────────────────────────────────────────

    def _route(self, user_input: str) -> str:
        """Route to Sovereign Core gateway → direct Ollama fallback."""
        history = self._memory.recent()
        # Build full prompt including history
        full_prompt = self._build_prompt(history, user_input)

        result = infer(
            prompt=full_prompt,
            system=self._system,
            model=self._cfg.get("model", "auto"),
            max_tokens=self._cfg.get("max_tokens", 1024),
            temperature=self._cfg.get("temperature", 0.7),
        )
        logger.debug(
            "Routed via %s | latency=%.0fms | tokens=%d",
            result.backend, result.latency_ms, result.tokens,
        )
        return result.text

    def _build_prompt(self, history: list[dict], current: str) -> str:
        """Build a conversation-formatted prompt string for Ollama."""
        lines = []
        # Include last N-1 turns from history (current not yet in history)
        for msg in history[:-1]:  # exclude the just-added current message
            role = msg["role"].upper()
            lines.append(f"[{role}]: {msg['content']}")
        lines.append(f"[USER]: {current}")
        lines.append("[ASSISTANT]:")
        return "\n".join(lines)


# ── SAGE-aware agent (extended for sovereign tasks) ───────────────────────────

class SovereignAgent(Agent):
    """
    Extended agent with direct access to KAIROS SAGE loop and ledger.
    Used by `python -m assistant.main sovereign` subcommands.
    """

    def run_sage(self, task: str) -> dict:
        """Submit a task to the SAGE 4-agent loop."""
        from assistant.core.sovereign_client import run_sage_task
        return run_sage_task(task)

    def evolve(self, cycles: int = 1) -> dict:
        """Trigger KAIROS evolution cycles."""
        import json, urllib.request
        from assistant.core.sovereign_client import GATEWAY_URL, _post
        return _post(f"{GATEWAY_URL}/kairos/evolve", {"cycles": cycles}, timeout=120)

    def ledger(self, n: int = 10) -> list:
        """Fetch recent Aegis-Vault ledger entries."""
        from assistant.core.sovereign_client import GATEWAY_URL, _get
        data = _get(f"{GATEWAY_URL}/ledger/tail?n={n}")
        return data.get("entries", [])
