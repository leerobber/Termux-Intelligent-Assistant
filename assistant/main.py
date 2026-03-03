"""
Entry point for the Termux Intelligent Assistant.

Usage:
    python -m assistant.main                  # start interactive chat
    python -m assistant.main config show      # show current settings
    python -m assistant.main config set KEY VALUE
    python -m assistant.main history clear    # clear conversation history
"""
import sys


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
