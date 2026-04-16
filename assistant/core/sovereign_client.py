"""
assistant/core/sovereign_client.py — Sovereign Core Gateway Client
Zero cloud SDK dependencies. Pure stdlib urllib.

Routes all inference through the local Heterogeneous Compute Gateway:
  RTX 5050 (localhost:8001) → Radeon 780M (localhost:8002) → Ryzen 7 (localhost:8003)

Falls back to direct Ollama if the gateway is unreachable.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────

GATEWAY_URL = "http://localhost:8000"
DIRECT_BACKENDS = [
    ("nvidia", "http://localhost:8001"),
    ("amd",    "http://localhost:8002"),
    ("cpu",    "http://localhost:8003"),
]
REQUEST_TIMEOUT = 30
HEALTH_CACHE_TTL = 20.0

_gateway_ok: bool = True
_last_health: float = 0.0


# ── Response ──────────────────────────────────────────────────────────────────

@dataclass
class InferenceResult:
    text: str
    model: str
    backend: str
    latency_ms: float
    tokens: int = 0
    fallback: bool = False


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _post(url: str, payload: dict, timeout: int = REQUEST_TIMEOUT) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _get(url: str, timeout: int = 5) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())


# ── Gateway health ────────────────────────────────────────────────────────────

def _check_gateway() -> bool:
    global _gateway_ok, _last_health
    now = time.time()
    if now - _last_health < HEALTH_CACHE_TTL:
        return _gateway_ok
    try:
        _get(f"{GATEWAY_URL}/health")
        _gateway_ok = True
    except Exception:
        _gateway_ok = False
    _last_health = now
    return _gateway_ok


# ── Inference ─────────────────────────────────────────────────────────────────

def infer(
    prompt: str,
    model: str = "auto",
    system: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> InferenceResult:
    """
    Route an inference request through the gateway, falling back to
    direct Ollama backend access if the gateway is unavailable.
    """
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    payload = {
        "model": model,
        "prompt": full_prompt,
        "options": {"num_predict": max_tokens, "temperature": temperature},
        "stream": False,
    }

    # Try gateway first
    if _check_gateway():
        try:
            t0 = time.time()
            data = _post(f"{GATEWAY_URL}/inference", payload)
            return InferenceResult(
                text=data.get("response", ""),
                model=data.get("model", model),
                backend=data.get("backend_id", "gateway"),
                latency_ms=(time.time() - t0) * 1000,
                tokens=data.get("eval_count", 0),
            )
        except Exception as exc:
            logger.warning("Gateway error: %s — trying direct backends", exc)

    # Direct backend fallback
    for name, url in DIRECT_BACKENDS:
        try:
            t0 = time.time()
            data = _post(f"{url}/api/generate", payload)
            return InferenceResult(
                text=data.get("response", ""),
                model=data.get("model", model),
                backend=f"direct:{name}",
                latency_ms=(time.time() - t0) * 1000,
                tokens=data.get("eval_count", 0),
                fallback=True,
            )
        except Exception as exc:
            logger.warning("Backend %s (%s) error: %s", name, url, exc)

    raise RuntimeError(
        "All inference backends unavailable. "
        "Is Sovereign Core running? (python -m uvicorn gateway.main:app --port 8000)"
    )


# ── SAGE loop access ──────────────────────────────────────────────────────────

def run_sage_task(task: str, context: Optional[dict] = None) -> dict:
    """
    Submit a task to the KAIROS SAGE 4-agent loop and return the result.
    Requires sovereign-core gateway to be running.
    """
    payload = {"task": task, "context": context or {}}
    try:
        return _post(f"{GATEWAY_URL}/kairos/sage", payload, timeout=120)
    except Exception as exc:
        raise RuntimeError(f"SAGE routing failed: {exc}") from exc


# ── Status ─────────────────────────────────────────────────────────────────────

def status() -> dict:
    """Return gateway status. Falls back gracefully if offline."""
    try:
        return _get(f"{GATEWAY_URL}/status/")
    except Exception:
        # Try each backend directly
        reachable = []
        for name, url in DIRECT_BACKENDS:
            try:
                _get(f"{url}/api/tags", timeout=3)
                reachable.append(name)
            except Exception:
                pass
        return {
            "gateway": "offline",
            "direct_backends_reachable": reachable,
            "message": "Gateway unreachable — using direct backend routing",
        }
