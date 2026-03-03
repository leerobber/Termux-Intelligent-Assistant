"""Termux Intelligent Assistant - Main entry point."""

import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

import config


# ---------------------------------------------------------------------------
# Provider helpers
# ---------------------------------------------------------------------------

def _chat_openai(messages: list[dict]) -> str:
    """Send messages to OpenAI and return the assistant reply."""
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai package not found. Run: pip install openai")

    if not config.OPENAI_API_KEY:
        sys.exit("OPENAI_API_KEY is not set. Edit config.env and try again.")

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=config.AI_MODEL,
        messages=messages,
        max_tokens=config.MAX_TOKENS,
        max_tokens=config.MAX_TOKENS,
    )
    return response.choices[0].message.content or ""


def _chat_anthropic(messages: list[dict]) -> str:
    """Send messages to Anthropic Claude and return the assistant reply."""
    try:
        import anthropic
    except ImportError:
        sys.exit("anthropic package not found. Run: pip install anthropic")

    if not config.ANTHROPIC_API_KEY:
        sys.exit("ANTHROPIC_API_KEY is not set. Edit config.env and try again.")

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Anthropic takes the system prompt separately
    response = client.messages.create(
        model=config.AI_MODEL,
        max_tokens=config.MAX_TOKENS,
        system=config.SYSTEM_PROMPT,
        messages=[m for m in messages if m["role"] != "system"],
    )
    return response.content[0].text if response.content else ""


def _chat_mistral(messages: list[dict]) -> str:
    """Send messages to Mistral AI and return the assistant reply."""
    try:
        from mistralai import Mistral
    except ImportError:
        sys.exit("mistralai package not found. Run: pip install mistralai")

    if not config.MISTRAL_API_KEY:
        sys.exit("MISTRAL_API_KEY is not set. Edit config.env and try again.")

    client = Mistral(api_key=config.MISTRAL_API_KEY)
    response = client.chat.complete(
        model=config.AI_MODEL,
        messages=messages,
        max_tokens=config.MAX_TOKENS,
    )
    return response.choices[0].message.content or ""


def _chat_llama(messages: list[dict]) -> str:
    """Send messages to Llama (via Groq) and return the assistant reply."""
    try:
        from groq import Groq
    except ImportError:
        sys.exit("groq package not found. Run: pip install groq")

    if not config.GROQ_API_KEY:
        sys.exit("GROQ_API_KEY is not set. Edit config.env and try again.")

    client = Groq(api_key=config.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=config.AI_MODEL,
        messages=messages,
        max_tokens=config.MAX_TOKENS,
    )
    return response.choices[0].message.content or ""


def chat(messages: list[dict]) -> str:
    """Route a conversation to the configured AI provider."""
    if config.AI_PROVIDER == "openai":
        return _chat_openai(messages)
    if config.AI_PROVIDER == "anthropic":
        return _chat_anthropic(messages)
    if config.AI_PROVIDER == "mistral":
        return _chat_mistral(messages)
    if config.AI_PROVIDER == "llama":
        return _chat_llama(messages)
    sys.exit(
        f"Unknown AI_PROVIDER '{config.AI_PROVIDER}'. "
        "Supported providers: openai, anthropic, mistral, llama."
    )


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

BANNER = """\
╔══════════════════════════════════════════════╗
║       Termux Intelligent Assistant           ║
║  Type your question or command.              ║
║  Type 'exit' or press Ctrl-D to quit.        ║
╚══════════════════════════════════════════════╝"""

PROMPT_STYLE = Style.from_dict({"prompt": "ansigreen bold"})


def run() -> None:
    """Start the interactive assistant REPL."""
    print(BANNER)
    print(f"  Provider : {config.AI_PROVIDER}")
    print(f"  Model    : {config.AI_MODEL}")
    print()

    session: PromptSession = PromptSession()
    messages: list[dict] = [{"role": "system", "content": config.SYSTEM_PROMPT}]

    while True:
        try:
            user_input = session.prompt("You> ", style=PROMPT_STYLE).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            reply = chat(messages)
        except Exception as exc:  # noqa: BLE001
            exc_type = type(exc).__name__
            print(f"[Error] {exc_type}: {exc}")
            print("[Hint] Check your API key, network connection, and model name in config.env.")
            # Remove the failed message so conversation state stays consistent
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": reply})
        print(f"\nAssistant> {reply}\n")


if __name__ == "__main__":
    run()
