"""
Entry point for the Termux Intelligent Assistant.

Usage:
    python -m assistant.main                  # start interactive chat
    python -m assistant.main config show      # show current settings
    python -m assistant.main config set KEY VALUE
    python -m assistant.main history clear    # clear conversation history
"""
import json
import logging
import re
import sys


def _extract_bash_blocks(text: str) -> list[str]:
    """Return a list of commands found inside ```bash … ``` fences in *text*."""
    return re.findall(r"```bash\s*(.*?)```", text, re.DOTALL)


def _coerce_value(key: str, raw: str):
    """Coerce *raw* string to the type expected for *key* based on DEFAULTS.

    Priority: bool → int → float → str (matching the default's type).
    For unknown keys or complex default types, falls back to json.loads.
    Raises ValueError with a user-friendly message on type mismatches.
    """
    from assistant.core.config import DEFAULTS

    if key in DEFAULTS:
        default = DEFAULTS[key]
        # bool must be checked before int (bool is a subclass of int)
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
                raise ValueError(
                    f"'{key}' expects an integer, got: {raw!r}"
                )
        if isinstance(default, float):
            try:
                return float(raw)
            except ValueError:
                raise ValueError(
                    f"'{key}' expects a float, got: {raw!r}"
                )
        if isinstance(default, str):
            return raw

    # Unknown key or non-primitive default: try JSON, fall back to string
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


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
            for msg in mem:
                role = msg["role"].upper()
                print(f"[{role}] {msg['content']}\n")


def _interactive() -> None:
    from assistant.core.agent import Agent
    from assistant.core.config import load as load_config
    from assistant.tools.shell import safe_run

    cfg = load_config()
    logging.basicConfig(level=getattr(logging, cfg.get("log_level", "WARNING"), logging.WARNING))

    print("Termux Intelligent Assistant  (type 'exit' or Ctrl-C to quit)\n")
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
            reply = agent.chat(user_input)
            print(f"\nAssistant: {reply}\n")

            bash_blocks = _extract_bash_blocks(reply)
            if bash_blocks:
                for block in bash_blocks:
                    block = block.strip()
                    if not block:
                        continue
                    indented = "\n".join(f"  {line}" for line in block.splitlines())
                    print(f"Suggested command:\n{indented}")
                    try:
                        choice = input("Run this command? [y/N] ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    if choice == "y":
                        result = safe_run(block)
                        if result.output:
                            print(result.output)
                        if not result.ok:
                            print(f"[exited with code {result.returncode}]")
                    print()


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]

    if args and args[0] == "config":
        _cmd_config(args[1:])
    elif args and args[0] == "history":
        _cmd_history(args[1:])
    else:
        _interactive()


if __name__ == "__main__":
    main()
