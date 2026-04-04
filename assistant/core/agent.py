"""
AI agent core — Sovereign Core edition.

Backends (in priority order):
  sovereign : Qwen2.5-32B-AWQ via OpenAI-compatible REST API
              (no API key, no cloud, full control — served by vLLM/litellm
               on TatorTot or localhost at port 8001)
  ollama    : local LLM via Ollama HTTP API (on-device, offline fallback)

Both backends support streaming to minimise peak RAM usage on mobile.
Zero third-party dependencies — uses only Python stdlib (urllib, json).
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Iterator

from assistant.core.config import load as load_config
from assistant.core.memory import Memory
from assistant.tools.system_info import get_context

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an intelligent assistant specialized in Termux and mobile Linux. "
    "Give concise, accurate answers. When suggesting shell commands, wrap them "
    "in ```bash ... ``` fences.\n\n"
    "{context}"
)


class Agent:
    """Stateful conversational agent with Sovereign Core and Ollama backends."""

    def __init__(self) -> None:
        self._cfg = load_config()
        self._memory = Memory(max_history=self._cfg["max_history"])
        self._backend: str = self._cfg["backend"]
        self._system_prompt = _SYSTEM_PROMPT.format(context=get_context())

    # ------------------------------------------------------------------
    def chat(self, user_input: str) -> str:
        """Send *user_input*, stream the reply, store both in memory."""
        self._memory.add("user", user_input)
        messages = self._build_messages()

        if self._backend == "sovereign":
            reply = self._sovereign(messages)
        elif self._backend == "ollama":
            reply = self._ollama(messages)
        else:
            reply = (
                f"Unknown backend '{self._backend}'. "
                "Set backend to 'sovereign' or 'ollama'.\n"
                "Run: python -m assistant.main config set backend sovereign"
            )

        self._memory.add("assistant", reply)
        return reply

    def chat_stream(self, user_input: str) -> Iterator[str]:
        """Stream tokens from *user_input*; yields each token as it arrives.

        Stores the full assembled reply in memory on completion.
        """
        self._memory.add("user", user_input)
        messages = self._build_messages()
        chunks: list[str] = []

        if self._backend == "sovereign":
            gen = self._sovereign_stream(messages)
        elif self._backend == "ollama":
            gen = self._ollama_stream(messages)
        else:
            error_msg = (
                f"Unknown backend '{self._backend}'. "
                "Set backend to 'sovereign' or 'ollama'."
            )
            yield error_msg
            self._memory.add("assistant", error_msg)
            return

        for token in gen:
            chunks.append(token)
            yield token

        full_reply = "".join(chunks)
        self._memory.add("assistant", full_reply)

    def clear_history(self) -> None:
        self._memory.clear()

    def close(self) -> None:
        self._memory.close()

    def status(self) -> dict[str, Any]:
        """Return a brief health-check dict for the configured backend."""
        result: dict[str, Any] = {
            "backend": self._backend,
            "reachable": False,
            "model": None,
        }
        try:
            if self._backend == "sovereign":
                url = self._cfg["sovereign_url"].rstrip("/") + "/v1/models"
                result["model"] = self._cfg["sovereign_model"]
            else:
                url = self._cfg["ollama_url"].rstrip("/") + "/api/tags"
                result["model"] = self._cfg["ollama_model"]
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5):
                result["reachable"] = True
        except Exception:
            pass
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_messages(self) -> list[dict[str, str]]:
        return [{"role": "system", "content": self._system_prompt}] + self._memory.recent()

    # ---------- Sovereign backend (OpenAI-compatible) -----------------

    def _sovereign(self, messages: list[dict[str, str]]) -> str:
        """Non-streaming sovereign request (collects full reply)."""
        return "".join(self._sovereign_stream(messages))

    def _sovereign_stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """Stream tokens from the Sovereign Core endpoint (SSE)."""
        url = self._cfg["sovereign_url"].rstrip("/") + "/v1/chat/completions"
        payload = json.dumps({
            "model": self._cfg["sovereign_model"],
            "messages": messages,
            "stream": True,
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._cfg.get("timeout", 60)) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    payload_str = line[len("data:"):].strip()
                    if payload_str == "[DONE]":
                        break
                    try:
                        data = json.loads(payload_str)
                        token = (
                            data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        continue
        except urllib.error.URLError as exc:
            url_display = self._cfg["sovereign_url"]
            yield (
                f"\n[Sovereign Core not reachable: {exc.reason}]\n"
                f"  Expected endpoint: {url_display}:8001\n"
                "  On TatorTot, start vLLM with:\n"
                "    vllm serve Qwen/Qwen2.5-32B-AWQ --port 8001\n"
                "  Then set your endpoint:\n"
                f"    python -m assistant.main config set sovereign_url http://<tatortot-ip>:8001\n"
                "  Or fall back to on-device Ollama:\n"
                "    python -m assistant.main config set backend ollama"
            )

    # ---------- Ollama backend ----------------------------------------

    def _ollama(self, messages: list[dict[str, str]]) -> str:
        """Non-streaming Ollama request (collects full reply)."""
        return "".join(self._ollama_stream(messages))

    def _ollama_stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """Stream tokens from the local Ollama endpoint."""
        url = self._cfg["ollama_url"].rstrip("/") + "/api/chat"
        payload = json.dumps({
            "model": self._cfg["ollama_model"],
            "messages": messages,
            "stream": True,
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._cfg.get("timeout", 60)) as resp:
                for raw_line in resp:
                    if not raw_line.strip():
                        continue
                    try:
                        data = json.loads(raw_line)
                        token = data.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except urllib.error.URLError as exc:
            yield (
                f"\n[Ollama not available: {exc.reason}]\n"
                "  Start Ollama:  ollama serve\n"
                f"  Pull a model:  ollama pull {self._cfg['ollama_model']}\n"
                "  Or point at TatorTot:\n"
                "    python -m assistant.main config set backend sovereign"
            )

    # ------------------------------------------------------------------
    def __enter__(self) -> "Agent":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
