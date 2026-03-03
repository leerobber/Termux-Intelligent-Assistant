#!/data/data/com.termux/files/usr/bin/bash
# Termux Intelligent Assistant - Setup Script
# Run this script inside Termux to install all dependencies.

set -e

echo "=== Termux Intelligent Assistant Setup ==="

# Update package list and upgrade existing packages
pkg update -y && pkg upgrade -y

# Install required Termux packages
echo "[*] Installing Termux packages..."
pkg install -y python python-pip git curl openssh

# Install Python dependencies
echo "[*] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create default config if it doesn't exist
if [ ! -f config.env ]; then
    echo "[*] Creating default config.env..."
    cat > config.env <<'EOF'
# Termux Intelligent Assistant Configuration
# Set your preferred AI provider API key below.

# OpenAI (https://platform.openai.com/account/api-keys)
OPENAI_API_KEY=

# Anthropic Claude (https://console.anthropic.com/)
ANTHROPIC_API_KEY=

# Which provider to use: "openai" or "anthropic"
AI_PROVIDER=openai

# Model name
# OpenAI examples:   gpt-4o, gpt-4o-mini, gpt-3.5-turbo
# Anthropic examples: claude-3-5-sonnet-20241022, claude-3-haiku-20240307
AI_MODEL=gpt-4o-mini

# Maximum tokens per response (default: 2048)
MAX_TOKENS=2048
EOF
    echo "[!] Edit config.env and add your API key before running the assistant."
fi

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Edit config.env and set your API key."
echo "  2. Run:  python assistant.py"
