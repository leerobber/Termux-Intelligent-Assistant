#!/data/data/com.termux/files/usr/bin/bash
# Termux Intelligent Assistant — Sovereign Core edition
# One-shot setup script. Run once after cloning: bash setup.sh
set -euo pipefail

cd "$(dirname "$0")"

CYAN='\033[96m'; BOLD='\033[1m'; GREEN='\033[92m'
YELLOW='\033[93m'; DIM='\033[2m'; RST='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════════╗${RST}"
echo -e "${BOLD}║  Termux Intelligent Assistant Setup      ║${RST}"
echo -e "${BOLD}║  Sovereign Core edition                  ║${RST}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${RST}"
echo ""

# ── 1. Update packages ────────────────────────────────────────────────────────
echo -e "${CYAN}[1/5] Updating packages...${RST}"
pkg update -y -q
pkg install -y -q python

# ── 2. Pip ────────────────────────────────────────────────────────────────────
echo -e "${CYAN}[2/5] Upgrading pip...${RST}"
python -m pip install --upgrade pip --quiet

# ── 3. Verify imports ─────────────────────────────────────────────────────────
echo -e "${CYAN}[3/5] Verifying installation...${RST}"
python - <<'PYEOF'
from assistant.core.config import load
from assistant.core.memory import Memory
from assistant.core.sovereign_client import GATEWAY_URL, DIRECT_BACKENDS
from assistant.utils.paths import ROOT
print(f"  Root: {ROOT}")
cfg = load()
print(f"  Backend:       {cfg.get('backend','sovereign')}")
print(f"  Sovereign URL: {cfg.get('sovereign_url', GATEWAY_URL)}")
print(f"  Ollama URL:    {cfg.get('ollama_url','http://localhost:11434')}")
print(f"  Model:         {cfg.get('model','auto')}")
print("  Import OK ✓")
PYEOF

# ── 4. Auto-detect Sovereign Core on LAN ──────────────────────────────────────
echo -e "${CYAN}[4/5] Scanning LAN for Sovereign Core gateway...${RST}"

FOUND_URL=""
GATEWAY_PORT=8000

# Get default gateway / router IP (likely the machine running Sovereign Core)
DEFAULT_GW=$(ip route | grep default | awk '{print $3}' 2>/dev/null || echo "")
SCAN_HOSTS=""

if [ -n "$DEFAULT_GW" ]; then
    # Build list of likely hosts (gateway, and .2/.3/.100)
    BASE=$(echo "$DEFAULT_GW" | cut -d. -f1-3)
    SCAN_HOSTS="$DEFAULT_GW $BASE.2 $BASE.3 $BASE.100 $BASE.200"
fi

for HOST in $SCAN_HOSTS; do
    URL="http://$HOST:$GATEWAY_PORT"
    STATUS=$(curl -s -m 2 "$URL/health" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || echo "")
    if [ "$STATUS" = "healthy" ] || [ "$STATUS" = "degraded" ]; then
        FOUND_URL="$URL"
        echo -e "  ${GREEN}Found Sovereign Core at $URL (status: $STATUS)${RST}"
        break
    fi
done

if [ -n "$FOUND_URL" ]; then
    python -m assistant.main config set sovereign_url "$FOUND_URL" 2>/dev/null || true
    echo -e "  ${GREEN}✓ Gateway URL auto-configured: $FOUND_URL${RST}"
else
    echo -e "  ${YELLOW}⚠  Gateway not found on LAN — using default localhost:8000${RST}"
    echo -e "  ${DIM}  Set manually: python -m assistant.main config set sovereign_url http://IP:8000${RST}"
fi

# ── 5. Final check ────────────────────────────────────────────────────────────
echo -e "${CYAN}[5/5] Running connectivity check...${RST}"
python -m assistant.main status 2>/dev/null || echo -e "  ${YELLOW}(Gateway offline — will use fallback)${RST}"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${RST}"
echo -e "${BOLD}║  Setup complete!                         ║${RST}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${RST}"
echo ""
echo -e "${DIM}Quick start:${RST}"
echo -e "  ${CYAN}python -m assistant.main${RST}              # start chat"
echo -e "  ${CYAN}python -m assistant.main status${RST}       # check connection"
echo -e "  ${CYAN}python -m assistant.main sovereign sage 'task'${RST}  # run SAGE"
echo ""
