# Termux Intelligent Assistant

An AI-powered assistant embedded directly in your **Termux** terminal. Ask it anything about Termux, Linux commands, shell scripting, package management, or programming — and get immediate, practical answers without leaving your terminal.

The assistant can brainstorm, draft, design, edit, create, build, and deploy, all from within your Termux environment.

---

## Features

- Interactive REPL chat interface inside Termux
- Supports **OpenAI** (GPT-4o, GPT-3.5-turbo, etc.), **Anthropic Claude** (claude-3-5-sonnet, etc.), **Mistral AI** (mistral-small, mistral-large, etc.), and **Llama** via Groq (llama-3.3-70b, llama3-8b, etc.)
- Remembers the conversation context within a session
- Simple `config.env` file for API key and model selection
- Lightweight — five Python dependencies

---

## Quick Start

### 1. Install Termux

Download [Termux from F-Droid](https://f-droid.org/packages/com.termux/) (recommended) or the Google Play Store.

### 2. Clone the repository

```bash
pkg install git -y
git clone https://github.com/leerobber/Termux-Intelligent-Assistant.git
cd Termux-Intelligent-Assistant
```

### 3. Run the setup script

```bash
bash setup.sh
```

This installs all required Termux packages and Python dependencies.

### 4. Add your API key

Open `config.env` in any editor (e.g. `nano config.env`) and paste in your API key:

```
# For OpenAI
OPENAI_API_KEY=sk-...

# Or for Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
AI_PROVIDER=anthropic

# Or for Mistral AI
MISTRAL_API_KEY=...
AI_PROVIDER=mistral
AI_MODEL=mistral-small-latest

# Or for Llama via Groq (free tier available)
GROQ_API_KEY=gsk_...
AI_PROVIDER=llama
AI_MODEL=llama-3.3-70b-versatile
```

### 5. Start the assistant

```bash
python assistant.py
```

---

## Configuration (`config.env`)

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `openai` | `openai`, `anthropic`, `mistral`, or `llama` |
| `AI_MODEL` | `gpt-4o-mini` | Model name for the chosen provider |
| `MAX_TOKENS` | `2048` | Maximum tokens in each response |
| `OPENAI_API_KEY` | *(empty)* | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | *(empty)* | Your Anthropic API key |
| `MISTRAL_API_KEY` | *(empty)* | Your Mistral AI API key |
| `GROQ_API_KEY` | *(empty)* | Your Groq API key (used for Llama models) |

### Provider model reference

| Provider | `AI_PROVIDER` | Example `AI_MODEL` values |
|---|---|---|
| OpenAI | `openai` | `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo` |
| Anthropic | `anthropic` | `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307` |
| Mistral AI | `mistral` | `mistral-small-latest`, `mistral-large-latest` |
| Llama (Groq) | `llama` | `llama-3.3-70b-versatile`, `llama3-8b-8192` |

---

## Project Structure

```
.
├── assistant.py     # Main entry point / interactive REPL
├── config.py        # Configuration loader
├── config.env       # Your local API keys and settings (not committed)
├── requirements.txt # Python dependencies
└── setup.sh         # One-shot Termux setup script
```

---

## Requirements

- Android device running [Termux](https://termux.dev/)
- Python 3.10+ (installed by `setup.sh`)
- An API key from [OpenAI](https://platform.openai.com/account/api-keys), [Anthropic](https://console.anthropic.com/), [Mistral AI](https://console.mistral.ai/), or [Groq](https://console.groq.com/keys) (for Llama)

---

## License

[MIT](LICENSE)
