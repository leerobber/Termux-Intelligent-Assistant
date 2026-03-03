"""Tests for the conversation Memory class."""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import assistant.core.memory as mem_mod  # noqa: E402


def _make_memory(tmp_path):
    db_path = tmp_path / "test_history.db"
    with mock.patch.object(mem_mod, "HISTORY_FILE", db_path), \
         mock.patch.object(mem_mod, "ensure_data_dir"):
        return mem_mod.Memory(max_history=5)


def test_add_and_recent(tmp_path):
    mem = _make_memory(tmp_path)
    mem.add("user", "Hello")
    mem.add("assistant", "Hi there!")
    messages = mem.recent()
    assert len(messages) == 2
    assert messages[0] == {"role": "user", "content": "Hello"}
    assert messages[1] == {"role": "assistant", "content": "Hi there!"}
    mem.close()


def test_max_history_enforced(tmp_path):
    mem = _make_memory(tmp_path)
    for i in range(10):
        mem.add("user", f"msg {i}")
    assert len(mem.recent()) <= 5
    mem.close()


def test_clear(tmp_path):
    mem = _make_memory(tmp_path)
    mem.add("user", "something")
    mem.clear()
    assert mem.recent() == []
    mem.close()


def test_context_manager(tmp_path):
    db_path = tmp_path / "ctx_history.db"
    with mock.patch.object(mem_mod, "HISTORY_FILE", db_path), \
         mock.patch.object(mem_mod, "ensure_data_dir"):
        with mem_mod.Memory(max_history=3) as mem:
            mem.add("user", "test")
            assert len(mem.recent()) == 1
