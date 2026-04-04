#!/data/data/com.termux/files/usr/bin/bash
# Termux Intelligent Assistant — Sovereign Core edition
# One-shot setup script.  Run once after cloning:  bash setup.sh
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Termux Intelligent Assistant (Sovereign Core) Setup ==="

# 1. Update package index
pkg update -y

# 2. Install Python
pkg install -y python

# 3. Upgrade pip (no cloud SDKs needed — stdlib only)
python -m pip install --upgrade pip

# 4. Verify the assistant can be imported
python - <<'PYEOF'
from assistant.core.config import load
from assistant.core.memory import Memory
from assistant.utils.paths import ROOT
print(f"Project root : {ROOT}")
cfg = load()
print(f"Backend      : {cfg['backend']}")
print(f"Sovereign URL: {cfg['sovereign_url']}")
print(f"Ollama URL   : {cfg['ollama_url']}")
print("Import OK!")
PYEOF

echo ""
echo "=== Setup complete ==="
echo ""
echo "Quick start:"
echo "  python -m assistant.main status          # check backend"
echo "  python -m assistant.main                 # start chat"
echo ""
echo "Connect to TatorTot (Sovereign Core):"
echo "  python -m assistant.main config set sovereign_url http://<tatortot-ip>:8001"
echo ""
echo "Fall back to on-device Ollama:"
echo "  pkg install ollama"
echo "  ollama serve &"
echo "  ollama pull tinyllama"
echo "  python -m assistant.main config set backend ollama"
