# Termux Intelligent Assistant

An agentic AI assistant built for **Termux on Android** — designed for low memory usage and written entirely in Python (no Node.js required).

The assistant can brainstorm, draft, design, edit, create, build, and deploy — all from within your Termux terminal.

---

## Why Python instead of Node.js?

Python is a more memory-efficient choice for resource-constrained mobile devices:

| Runtime | Idle RSS | Notes |
|---------|----------|-------|
| Node.js | ~50–80 MB | V8 JIT, large heap |
| Python  | ~8–15 MB | Lightweight interpreter |
| Shell   | ~1–3 MB  | Best for glue scripts |

This project uses **Python + stdlib only** by default — zero required third-party packages.

---

## Features

- **Local LLM via Ollama** — runs 100% on-device, no cloud required
- **Cloud providers** — OpenAI, **Anthropic Claude**, **Mistral AI**, and **Llama via Groq** (free tier available)
- **Relative paths everywhere** — no hardcoded `/data/data/...` or `/home/...` paths
- **SQLite conversation memory** — tiny footprint, survives restarts
- **Streaming responses** — low peak RAM usage
- **Shell tool** — ask the assistant to run Termux commands for you

---

## Quick Start (Termux)

```bash
# 1. Clone the repo
git clone https://github.com/leerobber/Termux-Intelligent-Assistant
cd Termux-Intelligent-Assistant

# 2. Run the one-shot setup (installs Python, Ollama, pulls tinyllama)
bash setup.sh

# 3. Start chatting
python -m assistant.main
```

---

## Project Structure

```
Termux-Intelligent-Assistant/
├── assistant/
│   ├── main.py              # Entry point & CLI
│   ├── core/
│   │   ├── agent.py         # AI agent (Ollama / OpenAI backends)
│   │   ├── config.py        # Settings loader (relative paths)
│   │   └── memory.py        # SQLite conversation history
│   ├── tools/
│   │   ├── shell.py         # Safe shell command execution
│   │   └── file_ops.py      # Relative-path file helpers
│   └── utils/
│       └── paths.py         # All path constants — no hardcoded paths
├── config/
│   └── settings.json        # User-editable settings
├── tests/                   # pytest test suite
├── requirements.txt         # Optional dependencies (stdlib works without them)
└── setup.sh                 # Termux one-shot setup script
```

All paths inside the codebase are **relative to the project root** (computed via `pathlib` at runtime). There are no hardcoded absolute paths.

---

## Configuration

```bash
# Show current settings
python -m assistant.main config show

# Switch to OpenAI backend
python -m assistant.main config set backend openai
python -m assistant.main config set openai_api_key sk-...

# Use a different Ollama model
python -m assistant.main config set ollama_model phi3

# Reduce history length to save RAM
python -m assistant.main config set max_history 10
```

### Available settings (`config/settings.json`)

| Key | Default | Description |
|-----|---------|-------------|
| `backend` | `"ollama"` | `"ollama"`, `"openai"`, `"mistral"`, `"anthropic"`, or `"llama"` |
| `ollama_model` | `"tinyllama"` | Local model name |
| `ollama_url` | `"http://localhost:11434"` | Ollama server URL |
| `openai_model` | `"gpt-4o-mini"` | OpenAI model name |
| `openai_api_key` | `""` | Your OpenAI API key |
| `mistral_model` | `"mistral-small-latest"` | Mistral AI model name |
| `mistral_api_key` | `""` | Your Mistral AI API key |
| `groq_model` | `"llama-3.3-70b-versatile"` | Llama model served by Groq |
| `groq_api_key` | `""` | Your Groq API key (for Llama models) |
| `anthropic_model` | `"claude-3-5-sonnet-20241022"` | Anthropic model name |
| `anthropic_api_key` | `""` | Your Anthropic API key |
| `anthropic_max_tokens` | `4096` | Max tokens in each Anthropic response |
| `max_history` | `20` | Max messages kept in memory |
| `stream` | `true` | Stream tokens for lower peak RAM |

### Provider model reference

| Provider | `backend` | Example model values |
|----------|-----------|----------------------|
| Ollama (local) | `ollama` | `tinyllama`, `phi3`, `llama3` |
| OpenAI | `openai` | `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo` |
| Mistral AI | `mistral` | `mistral-small-latest`, `mistral-large-latest` |
| Llama (Groq) | `llama` | `llama-3.3-70b-versatile`, `llama3-8b-8192` |
| Anthropic | `anthropic` | `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307` |

---

## Conversation History

```bash
# Show history
python -m assistant.main history

# Clear history
python -m assistant.main history clear
```

---

## Running Tests

```bash
# In Termux
pip install pytest
python -m pytest tests/ -v
```

---

## Memory-Saving Tips

1. **Use `tinyllama`** (default) — fits in 700 MB RAM
2. **Keep `max_history` low** (10 or less) on devices with < 4 GB RAM
3. **Enable streaming** (`"stream": true`) to avoid buffering large responses
4. **Use Ollama's `--num-ctx` flag** to reduce context window if needed:
   ```bash
   OLLAMA_NUM_CTX=512 ollama serve
   ```

---

## Efficient Termux Backend Alternatives to Node.js

| Option | Memory | Install | Best for |
|--------|--------|---------|----------|
| **Python** (this project) | ~10 MB | `pkg install python` | General scripting + AI |
| **Bash/sh** | ~2 MB | Pre-installed | Glue scripts, automation |
| **Lua** | ~1 MB | `pkg install lua54` | Embedded scripting |
| **Go** (compiled) | ~5 MB | `pkg install golang` | Performance-critical services |
| **Rust** (compiled) | ~3 MB | `pkg install rust` | Systems programming |

---

## License

See [LICENSE](LICENSE).

