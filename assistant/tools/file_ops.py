"""
File operation helpers — all paths are resolved via paths.py (relative to root).
Provides read, write, append, list, and delete helpers.
"""
from pathlib import Path
from typing import Optional

from assistant.utils.paths import resolve


def read(relative: str) -> str:
    """Read and return the text content of *relative* (relative to project root)."""
    return resolve(relative).read_text()


def write(relative: str, content: str) -> None:
    """Write *content* to *relative*, creating parent directories as needed."""
    p = resolve(relative)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def append(relative: str, content: str) -> None:
    """Append *content* to *relative*."""
    p = resolve(relative)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as fh:
        fh.write(content)


def delete(relative: str) -> bool:
    """Delete *relative*. Returns True if the file existed and was removed."""
    p = resolve(relative)
    if p.exists():
        p.unlink()
        return True
    return False


def list_files(relative: str = ".", pattern: str = "*") -> list[str]:
    """
    List files under *relative* matching *pattern*.
    Returns paths relative to the project root.
    """
    base = resolve(relative)
    root = resolve(".")
    return sorted(str(p.relative_to(root)) for p in base.glob(pattern) if p.is_file())
