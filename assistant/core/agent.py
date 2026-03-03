"""
AI agent core.

Supports four backends:
  - ollama  : local LLM via Ollama HTTP API (memory-efficient, works offline)
  - openai  : OpenAI API (requires internet + API key)
  - mistral : Mistral AI API (requires internet + API key)
  - llama   : Llama models via Groq API (requires internet + API key)

All backends use streaming or chunked responses to minimise peak RAM usage.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Iterator

from assistant.core.config import load as load_config
from assistant.core.memory import Memory

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an intelligent assistant specialized in Termux and mobile Linux. "
    "Give concise, accurate answers. When suggesting shell commands, wrap them "
    "in ```bash ... ``` fences."
)


class Agent:
    """Stateful conversational agent with pluggable backends."""

    def __init__(self) -> None:
        self._cfg = load_config()
        self._memory = Memory(max_history=self._cfg["max_history"])
        self._backend: str = self._cfg["backend"]

    # ------------------------------------------------------------------
    def chat(self, user_input: str) -> str:
        """Send *user_input*, stream the reply, store both in memory."""
        self._memory.add("user", user_input)
        messages = self._build_messages()

        if self._backend == "ollama":
            reply = self._ollama(messages)
        elif self._backend == "openai":
            reply = self._openai(messages)
        elif self._backend == "mistral":
            reply = self._mistral(messages)
        elif self._backend == "llama":
            reply = self._llama(messages)
        else:
            reply = (
                f"Unknown backend '{self._backend}'. "
                "Set backend to 'ollama', 'openai', 'mistral', or 'llama'."
            )

        self._memory.add("assistant", reply)
        return reply

    def clear_history(self) -> None:
        self._memory.clear()

    def close(self) -> None:
        self._memory.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_messages(self) -> list[dict[str, str]]:
        return [{"role": "system", "content": _SYSTEM_PROMPT}] + self._memory.recent()

    # ---------- Ollama backend ----------------------------------------

    def _ollama(self, messages: list[dict[str, str]]) -> str:
        url = self._cfg["ollama_url"].rstrip("/") + "/api/chat"
        payload = json.dumps(
            {
                "model": self._cfg["ollama_model"],
                "messages": messages,
                "stream": self._cfg.get("stream", True),
            }
        ).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        chunks: list[str] = []
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                for line in resp:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    chunks.append(token)
                    if data.get("done"):
                        break
        except urllib.error.URLError as exc:
            return (
                f"[Ollama not available: {exc.reason}]\n"
                "Start Ollama with: ollama serve\n"
                f"Pull a small model: ollama pull {self._cfg['ollama_model']}"
            )
        return "".join(chunks)

    # ---------- OpenAI backend ----------------------------------------

    def _openai(self, messages: list[dict[str, str]]) -> str:
        api_key = self._cfg.get("openai_api_key", "")
        if not api_key:
            return (
                "[OpenAI API key not set]\n"
                "Run: python -m assistant.main config set openai_api_key YOUR_KEY"
            )

        url = "https://api.openai.com/v1/chat/completions"
        payload = json.dumps(
            {
                "model": self._cfg["openai_model"],
                "messages": messages,
                "stream": False,
            }
        ).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            return f"[OpenAI HTTP error {exc.code}]: {exc.reason}"
        except urllib.error.URLError as exc:
            return f"[OpenAI connection error]: {exc.reason}"

    # ---------- Mistral backend ---------------------------------------

    def _mistral(self, messages: list[dict[str, str]]) -> str:
        api_key = self._cfg.get("mistral_api_key", "")
        if not api_key:
            return (
                "[Mistral API key not set]\n"
                "Run: python -m assistant.main config set mistral_api_key YOUR_KEY"
            )

        try:
            from mistralai import Mistral
        except ImportError:
            return (
                "[mistralai package not found]\n"
                "Run: python -m pip install mistralai"
            )

        try:
            client = Mistral(api_key=api_key)
            response = client.chat.complete(
                model=self._cfg["mistral_model"],
                messages=messages,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            return f"[Mistral error]: {exc}"

    # ---------- Llama (Groq) backend ----------------------------------

    def _llama(self, messages: list[dict[str, str]]) -> str:
        api_key = self._cfg.get("groq_api_key", "")
        if not api_key:
            return (
                "[Groq API key not set]\n"
                "Run: python -m assistant.main config set groq_api_key YOUR_KEY"
            )

        try:
            from groq import Groq
        except ImportError:
            return (
                "[groq package not found]\n"
                "Run: python -m pip install groq"
            )

        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=self._cfg["groq_model"],
                messages=messages,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            return f"[Groq error]: {exc}"

    # ------------------------------------------------------------------
    def __enter__(self) -> "Agent":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
