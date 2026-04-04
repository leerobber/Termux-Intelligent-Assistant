"""
Entry point for the Termux Intelligent Assistant — Sovereign Core edition.

Usage:
    python -m assistant.main                   # interactive chat (streaming)
    python -m assistant.main status            # check backend connectivity
    python -m assistant.main config show       # show current settings
    python -m assistant.main config set KEY VALUE
    python -m assistant.main history show      # display conversation history
    python -m assistant.main history clear     # clear conversation history
"""
from __future__ import annotations

import json
import logging
import re
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_bash_blocks(text: str) -> list[str]:
    """Return all commands found inside ```bash … ``` fences in *text*."""
    return re.findall(r"```bash\s*(.*?)```", text, re.DOTALL)


def _coerce_value(key: str, raw: str):
    """Coerce *raw* string to the type expected for *key* based on DEFAULTS."""
    from assistant.core.config import DEFAULTS

    if key in DEFAULTS:
        default = DEFAULTS[key]
        if isinstance(default, bool):
            raw_norm = raw.strip().lower()
            if raw_norm in ("true", "1", "yes"):
                return True
            if raw_norm in ("false", "0", "no"):
                return False
            raise ValueError(
                f"'{key}' expects a boolean (true/false/yes/no/1/0), got: {raw!r}"
            )
        if isinstance(default, int):
            try:
                return int(raw)
            except ValueError:
                raise ValueError(f"'{key}' expects an integer, got: {raw!r}")
        if isinstance(default, float):
            try:
                return float(raw)
            except ValueError:
                raise ValueError(f"'{key}' expects a float, got: {raw!r}")
        if isinstance(default, str):
            return raw

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

def _cmd_status() -> None:
    from assistant.core.agent import Agent

    with Agent() as agent:
        info = agent.status()
        backend = info["backend"]
        reachable = info["reachable"]
        model = info["model"]
        icon = "✓" if reachable else "✗"
        print(f"Backend : {backend}")
        print(f"Model   : {model}")
        print(f"Status  : {icon} {'reachable' if reachable else 'not reachable'}")
        if not reachable:
            if backend == "sovereign":
                print()
                print("  → Start vLLM on TatorTot:")
                print("      vllm serve Qwen/Qwen2.5-32B-AWQ --port 8001")
                print("  → Or fall back to on-device Ollama:")
                print("      python -m assistant.main config set backend ollama")
            else:
                print()
                print("  → Start Ollama:  ollama serve")


def _cmd_config(args: list[str]) -> None:
    from assistant.core.config import load, save

    settings = load()
    if not args or args[0] == "show":
        print(json.dumps(settings, indent=2))
    elif args[0] == "set" and len(args) >= 3:
        key, raw_value = args[1], args[2]
        try:
            value = _coerce_value(key, raw_value)
        except ValueError as exc:
            print(f"Error: {exc}")
            return
        settings[key] = value
        save(settings)
        print(f"Set {key} = {value!r}")
    else:
        print("Usage: python -m assistant.main config [show | set KEY VALUE]")


def _cmd_history(args: list[str]) -> None:
    from assistant.core.memory import Memory

    with Memory() as mem:
        if args and args[0] == "clear":
            mem.clear()
            print("History cleared.")
        else:
            messages = mem.recent()
            if not messages:
                print("No history.")
                return
            for msg in messages:
                role = msg["role"].upper()
                print(f"[{role}] {msg['content']}\n")


# ---------------------------------------------------------------------------
# Interactive loop
# ---------------------------------------------------------------------------

def _interactive() -> None:
    from assistant.core.agent import Agent
    from assistant.core.config import load as load_config
    from assistant.tools.shell import safe_run

    cfg = load_config()
    logging.basicConfig(
        level=getattr(logging, cfg.get("log_level", "WARNING"), logging.WARNING)
    )
    auto_run = cfg.get("auto_run_bash", False)
    use_stream = cfg.get("stream", True)

    print("Termux Intelligent Assistant — Sovereign Core")
    print(f"Backend: {cfg['backend']}  |  Model: {cfg.get('sovereign_model') if cfg['backend'] == 'sovereign' else cfg.get('ollama_model')}")
    print("Type 'exit' or Ctrl-C to quit, 'status' to check backend.\n")

    with Agent() as agent:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit", "bye"}:
                print("Goodbye!")
                break

            if user_input.lower() == "status":
                _cmd_status()
                print()
                continue

            if user_input.lower() == "history clear":
                agent.clear_history()
                print("History cleared.\n")
                continue

            print("\nAssistant: ", end="", flush=True)

            if use_stream:
                reply_parts: list[str] = []
                for token in agent.chat_stream(user_input):
                    print(token, end="", flush=True)
                    reply_parts.append(token)
                reply = "".join(reply_parts)
                print("\n")
            else:
                reply = agent.chat(user_input)
                print(reply + "\n")

            # ── Bash block detection ───────────────────────────────────────
            bash_blocks = _extract_bash_blocks(reply)
            if bash_blocks:
                for block in bash_blocks:
                    block = block.strip()
                    if not block:
                        continue

                    indented = "\n".join(f"  {line}" for line in block.splitlines())

                    if auto_run:
                        print(f"Auto-running:\n{indented}")
                        result = safe_run(block)
                    else:
                        print(f"Suggested command:\n{indented}")
                        try:
                            choice = input("Run? [y/N] ").strip().lower()
                        except (EOFError, KeyboardInterrupt):
                            print()
                            break
                        if choice != "y":
                            print()
                            continue
                        result = safe_run(block)

                    if result.output:
                        print(result.output)
                    if not result.ok:
                        print(f"[exited {result.returncode}]")
                    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]

    if args and args[0] == "status":
        _cmd_status()
    elif args and args[0] == "config":
        _cmd_config(args[1:])
    elif args and args[0] == "history":
        _cmd_history(args[1:])
    else:
        _interactive()


if __name__ == "__main__":
    main()
