"""
Entry point for the Termux Intelligent Assistant.

Usage:
    python -m assistant.main                  # start interactive chat
    python -m assistant.main config show      # show current settings
    python -m assistant.main config set KEY VALUE
    python -m assistant.main history clear    # clear conversation history
"""
import logging
import re
import sys


def _extract_bash_blocks(text: str) -> list[str]:
    """Return a list of commands found inside ```bash … ``` fences in *text*."""
    return re.findall(r"```bash\s*(.*?)```", text, re.DOTALL)


def _cmd_config(args: list[str]) -> None:
    from assistant.core.config import load, save

    settings = load()
    if not args or args[0] == "show":
        import json
        print(json.dumps(settings, indent=2))
    elif args[0] == "set" and len(args) >= 3:
        key, value = args[1], args[2]
        settings[key] = value
        save(settings)
        print(f"Set {key} = {value}")
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
