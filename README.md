# Termux Intelligent Assistant

> AI-embedded Termux assistant for Android terminal — powered by Sovereign Core.

Zero cloud SDK dependencies. Pure Python stdlib. Routes through your local GPU cluster or falls back to on-device Ollama.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│               Termux (Android terminal)              │
│                                                      │
│  python -m assistant.main                            │
│       │                                              │
│  ┌────▼────────────────┐                             │
│  │   Agent.chat()      │                             │
│  │   SQLite history    │                             │
│  └────┬────────────────┘                             │
│       │                                              │
│  ┌────▼────────────────────────────────────────┐    │
│  │         sovereign_client.py (stdlib)         │    │
│  │                                              │    │
│  │  1. Sovereign Core Gateway  :8000            │    │
│  │     ├── RTX 5050            :8001 (primary)  │    │
│  │     ├── Radeon 780M         :8002            │    │
│  │     └── Ryzen 7 CPU         :8003 (fallback) │    │
│  │                                              │    │
│  │  2. Direct Ollama (LAN)     :11434           │    │
│  │  3. Direct Ollama (device)  :11434           │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Install
pkg update -y && pkg install -y python
git clone https://github.com/leerobber/Termux-Intelligent-Assistant
cd Termux-Intelligent-Assistant
bash setup.sh

# Point at your Sovereign Core machine (TatorTot or local)
python -m assistant.main config set sovereign_url http://192.168.1.100:8000

# Start chat
python -m assistant.main
```

---

## Commands

```bash
# Interactive chat (default)
python -m assistant.main

# Backend connectivity check
python -m assistant.main status

# Configuration
python -m assistant.main config show
python -m assistant.main config set sovereign_url http://192.168.1.100:8000
python -m assistant.main config set model qwen2.5:14b
python -m assistant.main config set temperature 0.8

# History
python -m assistant.main history show
python -m assistant.main history clear
```

## Sovereign Core Subcommands

```bash
# Full gateway health
python -m assistant.main sovereign status

# Per-backend GPU details
python -m assistant.main sovereign backends

# Run a SAGE 4-agent task
python -m assistant.main sovereign sage "optimize vram allocation for qwen2.5:32b"

# Run KAIROS evolution cycles
python -m assistant.main sovereign evolve 5

# Tail Aegis-Vault ledger
python -m assistant.main sovereign ledger 20
```

---

## Configuration

Settings stored in `config/settings.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `backend` | `sovereign` | Primary backend: sovereign \| ollama |
| `sovereign_url` | `http://localhost:8000` | Sovereign Core gateway URL |
| `ollama_url` | `http://localhost:11434` | Direct Ollama URL (fallback) |
| `model` | `auto` | Model ID or `auto` for gateway selection |
| `max_history` | `20` | Conversation turns to keep in SQLite |
| `max_tokens` | `1024` | Max tokens per response |
| `temperature` | `0.7` | Sampling temperature |
| `stream` | `false` | Enable streaming output |

---

## Connect to TatorTot (Sovereign Core)

```bash
# Set gateway URL to your machine's LAN IP
python -m assistant.main config set sovereign_url http://192.168.1.XXX:8000

# Verify connection
python -m assistant.main sovereign status

# Expected output:
#   Gateway: ONLINE  uptime 04:22:17
#
#   GPU Backends:
#     ● rtx5050           42ms
#     ● radeon780m        89ms
#     ● ryzen7cpu        180ms
```

---

## Fallback Chain

1. **Sovereign Core Gateway** — sends request to gateway, which routes across your GPU cluster
2. **Direct Ollama (LAN)** — if gateway unreachable, hits Ollama directly on the configured host
3. **Direct CPU backend** — last resort, Ollama on :8003

No cloud. No API keys. Full local inference.

---

## Zero Dependencies

Uses only Python stdlib:
- `urllib.request` — HTTP requests
- `sqlite3` — conversation history
- `json` — config + API responses
- `pathlib` — cross-platform paths

---

## License

MIT
