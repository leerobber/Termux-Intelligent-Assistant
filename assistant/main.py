"""
assistant/main.py — Termux Intelligent Assistant (Sovereign Core edition)
=========================================================================
Usage:
    python -m assistant.main                        # interactive chat
    python -m assistant.main status                 # backend connectivity
    python -m assistant.main config show            # current settings
    python -m assistant.main config set KEY VALUE   # change a setting
    python -m assistant.main history show           # conversation history
    python -m assistant.main history clear          # clear history

    # Sovereign Core subcommands
    python -m assistant.main sovereign status       # gateway + backend health
    python -m assistant.main sovereign sage "task"  # run SAGE 4-agent loop
    python -m assistant.main sovereign evolve [N]   # run N ARSO cycles
    python -m assistant.main sovereign ledger [N]   # tail N ledger entries
    python -m assistant.main sovereign backends     # per-backend details
"""
from __future__ import annotations

import json
import logging
import re
import sys
from typing import Any

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# ── ANSI colors (Termux supports them) ───────────────────────────────────────

C = {
    "g": "\033[92m", "y": "\033[93m", "r": "\033[91m",
    "c": "\033[96m", "b": "\033[94m", "bold": "\033[1m",
    "dim": "\033[2m", "rst": "\033[0m",
}


def col(code: str, text: str) -> str:
    return f"{C[code]}{text}{C['rst']}"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _bash_blocks(text: str) -> list[str]:
    return re.findall(r"```bash\s*(.*?)```", text, re.DOTALL)


def _coerce(key: str, raw: str) -> Any:
    from assistant.core.config import DEFAULTS
    if key in DEFAULTS:
        default = DEFAULTS[key]
        if isinstance(default, bool):
            return raw.strip().lower() in ("true", "1", "yes")
        if isinstance(default, int):
            return int(raw)
        if isinstance(default, float):
            return float(raw)
    return raw


# ── Interactive chat ───────────────────────────────────────────────────────────

def run_chat() -> None:
    from assistant.core.agent import Agent
    agent = Agent()

    print(col("bold", "\n╔══════════════════════════════════════════╗"))
    print(col("bold",   "║  Termux Intelligent Assistant            ║"))
    print(col("bold",   "║  Powered by Sovereign Core               ║"))
    print(col("bold",   "╚══════════════════════════════════════════╝"))
    print(col("dim",  "  Type 'exit' or Ctrl-C to quit\n"))

    while True:
        try:
            user = input(col("c", "you › ")).strip()
        except (EOFError, KeyboardInterrupt):
            print(col("dim", "\nGoodbye."))
            break

        if not user:
            continue
        if user.lower() in ("exit", "quit", "q"):
            print(col("dim", "Goodbye."))
            break

        print(col("dim", "thinking…"), end="\r", flush=True)
        reply = agent.chat(user)
        print(" " * 12, end="\r")  # clear "thinking..."
        print(f"\n{col('bold', 'assistant')} › {reply}\n")

        # Highlight bash blocks
        for cmd in _bash_blocks(reply):
            print(col("y", f"  $ {cmd.strip()}"))
        if _bash_blocks(reply):
            print()


# ── Status command ─────────────────────────────────────────────────────────────

def run_status() -> None:
    from assistant.core.sovereign_client import status
    data = status()

    if data.get("gateway") == "offline":
        print(col("y", "⚠  Gateway offline"))
        reachable = data.get("direct_backends_reachable", [])
        if reachable:
            print(f"   Direct backends reachable: {', '.join(reachable)}")
        else:
            print(col("r", "   No backends reachable. Is Ollama running?"))
        return

    uptime = data.get("uptime_s", 0)
    h, rem = divmod(int(uptime), 3600)
    m, s = divmod(rem, 60)
    print(col("bold", f"\n  Gateway: {col('g', 'ONLINE')}  uptime {h:02d}:{m:02d}:{s:02d}"))

    backends = data.get("backends", [])
    if backends:
        print(col("bold", "\n  GPU Backends:"))
        for b in backends:
            dot = col("g", "●") if b.get("healthy") else col("r", "●")
            lat_raw = b.get("latency_ms")
            lat = f"{lat_raw:.0f}ms" if lat_raw is not None else "—"
            print(f"    {dot} {b.get('name','?'):18s} {lat:>7s}")
    print()


# ── Config commands ────────────────────────────────────────────────────────────

def run_config(args: list[str]) -> None:
    from assistant.core.config import load, save

    if not args or args[0] == "show":
        cfg = load()
        print(col("bold", "\n  Current configuration:\n"))
        for k, v in sorted(cfg.items()):
            print(f"    {k:30s} = {v}")
        print()
        return

    if args[0] == "set" and len(args) >= 3:
        key, raw = args[1], " ".join(args[2:])
        cfg = load()
        try:
            value = _coerce(key, raw)
            cfg[key] = value
            save(cfg)
            print(col("g", f"  ✓ {key} = {value}"))
        except (ValueError, TypeError) as e:
            print(col("r", f"  ✗ {e}"))
        return

    print(col("r", f"  Unknown config command: {' '.join(args)}"))
    print("  Usage: config show | config set KEY VALUE")


# ── History commands ───────────────────────────────────────────────────────────

def run_history(args: list[str]) -> None:
    from assistant.core.memory import Memory

    memory = Memory()
    if not args or args[0] == "show":
        messages = memory.recent()
        if not messages:
            print(col("dim", "  No history yet."))
            return
        print(col("bold", f"\n  Last {len(messages)} messages:\n"))
        for msg in messages:
            role_col = "c" if msg["role"] == "user" else "g"
            print(f"  {col(role_col, msg['role']:12s)} {msg['content'][:120]}")
        print()

    elif args[0] == "clear":
        memory.clear()
        print(col("g", "  ✓ History cleared."))


# ── Sovereign subcommands ──────────────────────────────────────────────────────

def run_sovereign(args: list[str]) -> None:
    if not args:
        print("Usage: sovereign status | sage TASK | evolve [N] | ledger [N] | backends")
        return

    subcmd = args[0]

    if subcmd == "status":
        run_status()

    elif subcmd == "backends":
        from assistant.core.sovereign_client import GATEWAY_URL, _get
        try:
            data = _get(f"{GATEWAY_URL}/status/backends")
            print(col("bold", "\n  GPU Backend Details:\n"))
            for name, info in data.items():
                dot = col("g", "●") if info.get("healthy") else col("r", "●")
                lat = info.get("latency_ms")
                lat_str = f"{lat:.1f}ms" if lat else "—"
                print(f"  {dot} {name}")
                print(f"      URL:    {info.get('url','?')}")
                print(f"      Device: {info.get('device_type','?')}")
                print(f"      Lat:    {lat_str}")
        except Exception as e:
            print(col("r", f"  ✗ {e}"))

    elif subcmd == "sage":
        task = " ".join(args[1:]) if len(args) > 1 else "optimize performance"
        print(col("c", f"  ⟳ Running SAGE loop: {task[:60]}..."))
        from assistant.core.sovereign_client import run_sage_task
        try:
            result = run_sage_task(task)
            print(f"\n  Agent:   {result.get('agent_id','?')}")
            print(f"  Score:   {result.get('score', 0):.3f}")
            print(f"  Verdict: {result.get('verification_verdict','?')}")
            proposals = result.get("proposals", [])
            if proposals:
                print(f"\n  Best proposal:\n  {proposals[0][:300]}")
        except Exception as e:
            print(col("r", f"  ✗ SAGE failed: {e}"))

    elif subcmd == "evolve":
        cycles = int(args[1]) if len(args) > 1 else 1
        print(col("c", f"  ⟳ Running {cycles} evolution cycle(s)..."))
        from assistant.core.sovereign_client import GATEWAY_URL, _post
        try:
            data = _post(f"{GATEWAY_URL}/kairos/evolve", {"cycles": cycles}, timeout=120)
            for r in data.get("results", []):
                promoted = col("y", " 🌟 ELITE") if r.get("elite_promoted") else ""
                print(
                    f"  gen={r['generation']}  "
                    f"score={r['score']:.3f}  "
                    f"verdict={r['verification_verdict']}"
                    f"{promoted}"
                )
        except Exception as e:
            print(col("r", f"  ✗ Evolution failed: {e}"))

    elif subcmd == "ledger":
        n = int(args[1]) if len(args) > 1 else 10
        from assistant.core.sovereign_client import GATEWAY_URL, _get
        try:
            data = _get(f"{GATEWAY_URL}/ledger/tail?n={n}")
            entries = data.get("entries", [])
            print(col("bold", f"\n  Aegis-Vault — Last {len(entries)} entries:\n"))
            for e in entries:
                import time
                ts = time.strftime("%H:%M:%S", time.localtime(e.get("timestamp", 0)))
                op = e.get("operation_type", "?")
                trust = e.get("trust_score", 0)
                ok = col("g", "✓") if e.get("integrity_ok") else col("r", "✗")
                print(f"  {ts}  {ok}  {op:28s}  trust={trust:.3f}")
        except Exception as e:
            print(col("r", f"  ✗ Ledger failed: {e}"))

    else:
        print(col("r", f"  Unknown sovereign subcommand: {subcmd}"))


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    argv = sys.argv[1:]

    if not argv:
        run_chat()
        return

    cmd = argv[0]
    rest = argv[1:]

    dispatch = {
        "status":    lambda: run_status(),
        "config":    lambda: run_config(rest),
        "history":   lambda: run_history(rest),
        "sovereign": lambda: run_sovereign(rest),
    }

    fn = dispatch.get(cmd)
    if fn:
        fn()
    else:
        print(col("r", f"Unknown command: {cmd}"))
        print("Commands: status | config | history | sovereign")
        sys.exit(1)


if __name__ == "__main__":
    main()
