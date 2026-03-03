#!/data/data/com.termux/files/usr/bin/bash
# Termux Intelligent Assistant — one-shot setup script
# Run once after cloning:  bash setup.sh
set -euo pipefail

# Change to the directory where this script lives so all relative paths work
# correctly regardless of the working directory when the script is invoked.
cd "$(dirname "$0")"

echo "=== Termux Intelligent Assistant Setup ==="

# 1. Update package index
pkg update -y

# 2. Install Python (memory-efficient alternative to Node.js)
pkg install -y python

# 3. Install Ollama for local LLM inference (runs on-device, no cloud needed)
#    https://ollama.com/download/linux
if ! command -v ollama &>/dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 4. Pull a small model that fits in mobile RAM (~700 MB)
echo "Pulling tinyllama model (smallest, fastest)..."
ollama pull tinyllama

# 5. Install Python deps (anthropic, mistralai and groq required for those backends)
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
    # Strip comment lines before installing
    grep -v '^\s*#' requirements.txt | grep -v '^\s*$' | python -m pip install -r /dev/stdin || true
fi

# 6. Verify the assistant can be imported
python - <<'PYEOF'
from assistant.core.config import load
from assistant.core.memory import Memory
from assistant.utils.paths import ROOT
print(f"Project root : {ROOT}")
print(f"Config loaded: {load()['backend']} backend")
print("Setup OK!")
PYEOF
