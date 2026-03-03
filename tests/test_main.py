"""Tests for assistant.main helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant.main import _extract_bash_blocks  # noqa: E402


def test_extract_single_block():
    text = "Try this:\n```bash\necho hello\n```"
    blocks = _extract_bash_blocks(text)
    assert blocks == ["echo hello\n"]


def test_extract_multiple_blocks():
    text = (
        "First:\n```bash\npkg update\n```\n"
        "Then:\n```bash\npkg install python\n```"
    )
    blocks = _extract_bash_blocks(text)
    assert len(blocks) == 2
    assert "pkg update" in blocks[0]
    assert "pkg install python" in blocks[1]


def test_extract_no_blocks():
    text = "There are no commands here, just plain text."
    assert _extract_bash_blocks(text) == []


def test_extract_ignores_non_bash_fences():
    text = "```python\nprint('hello')\n```"
    assert _extract_bash_blocks(text) == []


def test_extract_multiline_block():
    text = "```bash\napt update\napt upgrade -y\n```"
    blocks = _extract_bash_blocks(text)
    assert len(blocks) == 1
    assert "apt update" in blocks[0]
    assert "apt upgrade -y" in blocks[0]


def test_extract_block_without_trailing_newline():
    text = "```bash\necho hi```"
    blocks = _extract_bash_blocks(text)
    assert len(blocks) == 1
    assert "echo hi" in blocks[0]
