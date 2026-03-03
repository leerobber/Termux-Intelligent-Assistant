"""Tests for the file_ops tool."""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import assistant.utils.paths as paths_mod  # noqa: E402
import assistant.tools.file_ops as file_ops  # noqa: E402


def test_write_and_read(tmp_path):
    with mock.patch.object(paths_mod, "ROOT", tmp_path):
        file_ops.write("docs/note.txt", "hello world")
        assert file_ops.read("docs/note.txt") == "hello world"


def test_append(tmp_path):
    with mock.patch.object(paths_mod, "ROOT", tmp_path):
        file_ops.write("test.txt", "line1\n")
        file_ops.append("test.txt", "line2\n")
        content = file_ops.read("test.txt")
        assert "line1" in content and "line2" in content


def test_delete(tmp_path):
    with mock.patch.object(paths_mod, "ROOT", tmp_path):
        file_ops.write("del_me.txt", "bye")
        assert file_ops.delete("del_me.txt") is True
        assert not (tmp_path / "del_me.txt").exists()
        # Deleting again returns False
        assert file_ops.delete("del_me.txt") is False


def test_list_files(tmp_path):
    with mock.patch.object(paths_mod, "ROOT", tmp_path):
        file_ops.write("a.txt", "a")
        file_ops.write("b.txt", "b")
        files = file_ops.list_files(".", "*.txt")
        assert "a.txt" in files
        assert "b.txt" in files
