# Termux Intelligent Assistant

> *A fully autonomous AI agent living inside your Android terminal — works offline, upgrades when home.*

[![Python](https://img.shields.io/badge/Python-stdlib_only-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Android](https://img.shields.io/badge/Android-Termux-3ddc84?style=flat-square&logo=android&logoColor=white)](https://termux.dev)
[![Sovereign Core](https://img.shields.io/badge/Sovereign_Core-WiFi_connected-00ff88?style=flat-square)](https://github.com/leerobber/sovereign-core)
[![Offline](https://img.shields.io/badge/Offline-capable-ff6b35?style=flat-square)](https://github.com/leerobber/Termux-Intelligent-Assistant)

---

## What This Is

Termux Intelligent Assistant is an **autonomous AI agent that lives inside your Android terminal** — no cloud dependencies, no API keys required, no internet needed to run.

On WiFi at home → routes inference through the **Sovereign Core gateway** on your local GPU cluster (RTX 5050 / Radeon 780M / Ryzen CPU).

Away from home → falls back to on-device Ollama. Still fully functional. Still fully local.

Zero external SDK dependencies. Pure Python stdlib. If Termux can run it, this runs.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│              TERMUX (Android Terminal)               │
│                                                      │
│   python -m assistant.main                           │
│         │                                            │
│   ┌─────▼──────────────────────────────────────┐    │
│   │          ROUTING LAYER                      │    │
│   │                                             │    │
│   │   Home WiFi detected?                       │    │
│   │   YES ──► Sovereign Core Gateway :8000      │    │
│   │           RTX 5050 / Radeon / Ryzen CPU     │    │
│   │                                             │    │
│   │   NO  ──► On-device Ollama (local fallback) │    │
│   │           Runs on phone CPU/GPU             │    │
│   └─────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## What It Can Do

- **Brainstorm** — think through problems, generate ideas, explore concepts
- **Draft** — write code, documentation, messages, plans
- **Design** — architect systems, plan implementations, diagram structures
- **Edit** — review and improve existing code or text
- **Create** — build scripts, tools, and utilities directly in terminal
- **Build** — scaffold projects, generate boilerplate, set up environments
- **Deploy** — automate deployment steps, manage processes
- **Teach** — explain anything about Termux, Linux, Python, AI — right in the terminal

All of it. No browser. No GUI. Pure terminal.

---

## Sovereign Core Integration

```python
# sovereign_client.py — zero external dependencies
import urllib.request, json, os

GATEWAY = os.environ.get("SOVEREIGN_GATEWAY_URL", "http://192.168.x.x:8000")

def query(prompt: str) -> str:
    """Route to sovereign-core gateway — pure stdlib, no requests library."""
    payload = json.dumps({
        "model": "qwen2.5",
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    
    req = urllib.request.Request(
        f"{GATEWAY}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]
```

No `pip install` required. No external libraries. Just Python.

---

## Quickstart

```bash
# Install Termux from F-Droid (not Play Store)
# Then inside Termux:

pkg update && pkg upgrade
pkg install python git

git clone https://github.com/leerobber/Termux-Intelligent-Assistant
cd Termux-Intelligent-Assistant

# Configure sovereign gateway (your home IP)
cp .env.example .env
# Set SOVEREIGN_GATEWAY_URL=http://192.168.x.x:8000

# Run
python -m assistant.main
```

---

## Why Pure Stdlib?

Termux has constraints. Package installs fail. Environments break. Dependencies conflict.

Pure stdlib means this **always runs** — on any Android device, any Termux version, any Python 3.6+, with or without internet, with or without pip working.

The constraint became the design principle.

---

## Part of the Sovereign Stack

| Repo | Role |
|------|------|
| [sovereign-core](https://github.com/leerobber/sovereign-core) | Gateway + KAIROS engine — what this connects to on WiFi |
| [DGM](https://github.com/leerobber/DGM) | Darwin Gödel Machine |
| [HyperAgents](https://github.com/leerobber/HyperAgents) | Self-referential swarm agents |
| [Honcho](https://github.com/leerobber/Honcho) | Mission control dashboard |
| [contentai-pro](https://github.com/leerobber/contentai-pro) | Multi-agent content engine |
| **Termux-Intelligent-Assistant** | Mobile terminal agent — sovereign on the go |

---

## Built By

**Terry Lee** — Douglasville, GA
Self-taught systems architect. Fabrication worker by day. AI infrastructure builder by night.
No institution. No team. Just architecture.

*Self-taught. Self-funded. Self-improving — just like the systems I build.*
