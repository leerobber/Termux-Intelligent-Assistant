# Termux Intelligent Assistant — Sovereign Core Edition

An agentic AI assistant for Termux (Android) and mobile Linux, powered by
**Sovereign Core** — your own locally-hosted Qwen2.5-32B-AWQ model running
on TatorTot. No cloud APIs. No API keys. No data leaving your network.

## Architecture

```
Termux (LOQ Laptop / Android Phone)
        │
        │  OpenAI-compatible REST  (LAN or localhost)
        ▼
TatorTot  ←→  vLLM serving Qwen2.5-32B-AWQ @ :8001
        │
        └── Sovereign Core (HyperAgents, VAGEN, …)
```

**Backends (in priority order):**
| Backend    | Model                   | Where it runs          |
|------------|-------------------------|------------------------|
| `sovereign`| Qwen2.5-32B-AWQ         | TatorTot / localhost   |
| `ollama`   | tinyllama (or any model)| On-device (offline)    |

Zero cloud SDK dependencies — the `sovereign` backend uses stdlib `urllib`
against the same OpenAI-compatible endpoint that HyperAgents uses.

---

## Quick Start

```bash
git clone https://github.com/leerobber/Termux-Intelligent-Assistant.git
cd Termux-Intelligent-Assistant
bash setup.sh
```

### Point at TatorTot

```bash
python -m assistant.main config set sovereign_url http://192.168.x.x:8001
python -m assistant.main status   # verify connection
python -m assistant.main          # start chat
```

### Use on-device Ollama (offline fallback)

```bash
pkg install ollama
ollama serve &
ollama pull tinyllama
python -m assistant.main config set backend ollama
```

---

## Usage

```
python -m assistant.main                    # interactive chat (streaming)
python -m assistant.main status             # check backend connectivity
python -m assistant.main config show        # show all settings
python -m assistant.main config set KEY VAL # update a setting
python -m assistant.main history show       # view conversation history
python -m assistant.main history clear      # clear conversation history
```

### Key Settings

| Key               | Default                       | Description                           |
|-------------------|-------------------------------|---------------------------------------|
| `backend`         | `sovereign`                   | Active backend (`sovereign`/`ollama`) |
| `sovereign_url`   | `http://localhost:8001`       | Sovereign Core endpoint               |
| `sovereign_model` | `openai/qwen2.5-32b-awq`      | Model identifier                      |
| `ollama_url`      | `http://localhost:11434`      | Ollama endpoint                       |
| `ollama_model`    | `tinyllama`                   | Ollama model name                     |
| `stream`          | `true`                        | Stream tokens as they arrive          |
| `auto_run_bash`   | `false`                       | Auto-execute AI-suggested commands    |
| `max_history`     | `20`                          | Messages kept in rolling SQLite log   |
| `timeout`         | `60`                          | Request timeout (seconds)             |

---

## Features

- **Sovereign-first** — Qwen2.5-32B-AWQ via local OpenAI-compatible API
- **Streaming output** — tokens printed as they arrive, minimal RAM usage
- **Agentic bash** — AI-suggested commands shown with run prompt (or auto-run)
- **Persistent memory** — SQLite rolling conversation window
- **System context** — device info (CPU, RAM, storage, Termux paths) injected into every prompt
- **Status check** — `python -m assistant.main status` verifies backend reachability
- **Zero cloud deps** — stdlib urllib only; `requirements.txt` has no mandatory packages
- **Config CLI** — set any option from the terminal, persisted to `config/settings.json`

---

## Project Structure

```
assistant/
├── core/
│   ├── agent.py          # sovereign + ollama backends, streaming
│   ├── config.py         # settings loader with type coercion
│   └── memory.py         # SQLite rolling conversation history
├── main.py               # CLI entry point, interactive loop
├── tools/
│   ├── file_ops.py       # file read/write operations
│   ├── shell.py          # shell command execution
│   └── system_info.py    # device/Termux context for system prompt
└── utils/
    └── paths.py          # project-relative path resolution
config/settings.json      # runtime configuration (gitignored in practice)
requirements.txt          # optional dependencies only
setup.sh                  # one-shot Termux setup
```

---

## Part of Sovereign Core

This assistant is the mobile/Termux interface to the Sovereign Core ecosystem.

| Repo | Role |
|------|------|
| [sovereign-core](https://github.com/leerobber/sovereign-core) | Project tracking, issues, roadmap |
| [HyperAgents](https://github.com/leerobber/HyperAgents) | Self-evolving agent loop (rewired to Qwen2.5) |
| [VAGEN](https://github.com/leerobber/VAGEN) | Vision-language agent training |
| **Termux-Intelligent-Assistant** | Mobile terminal interface → Sovereign Core |

---

## License

MIT — see [LICENSE](LICENSE)
