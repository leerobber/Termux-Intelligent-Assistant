"""Tests for assistant.main helpers."""
import json
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant.main import _coerce_value, _cmd_config, _extract_bash_blocks  # noqa: E402


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


# ---------------------------------------------------------------------------
# _coerce_value tests
# ---------------------------------------------------------------------------

def test_coerce_int_key():
    assert _coerce_value("max_history", "5") == 5
    assert isinstance(_coerce_value("max_history", "5"), int)


def test_coerce_int_invalid_raises():
    with pytest.raises(ValueError, match="integer"):
        _coerce_value("max_history", "abc")


def test_coerce_bool_true_variants():
    for raw in ("true", "True", "TRUE", "1", "yes", "Yes", " true ", "true "):
        result = _coerce_value("stream", raw)
        assert result is True, f"Expected True for {raw!r}"


def test_coerce_bool_false_variants():
    for raw in ("false", "False", "FALSE", "0", "no", "No", " false ", "false "):
        result = _coerce_value("stream", raw)
        assert result is False, f"Expected False for {raw!r}"


def test_coerce_bool_invalid_raises():
    with pytest.raises(ValueError, match="boolean"):
        _coerce_value("stream", "maybe")


def test_coerce_str_key_returns_string():
    result = _coerce_value("backend", "openai")
    assert result == "openai"
    assert isinstance(result, str)


def test_coerce_unknown_key_json_list():
    result = _coerce_value("unknown_key", "[1,2,3]")
    assert result == [1, 2, 3]


def test_coerce_unknown_key_json_dict():
    result = _coerce_value("unknown_key", '{"a": 1}')
    assert result == {"a": 1}


def test_coerce_unknown_key_plain_string():
    result = _coerce_value("unknown_key", "hello")
    assert result == "hello"


# ---------------------------------------------------------------------------
# _cmd_config integration tests
# ---------------------------------------------------------------------------

def test_cmd_config_set_int(tmp_path, capsys):
    settings_file = tmp_path / "settings.json"
    import assistant.core.config as cfg_mod

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        _cmd_config(["set", "max_history", "7"])

    saved = json.loads(settings_file.read_text())
    assert saved["max_history"] == 7
    assert isinstance(saved["max_history"], int)
    captured = capsys.readouterr()
    assert "max_history" in captured.out


def test_cmd_config_set_bool(tmp_path, capsys):
    settings_file = tmp_path / "settings.json"
    import assistant.core.config as cfg_mod

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        _cmd_config(["set", "stream", "false"])

    saved = json.loads(settings_file.read_text())
    assert saved["stream"] is False
    captured = capsys.readouterr()
    assert "stream" in captured.out


def test_cmd_config_set_invalid_int_prints_error(tmp_path, capsys):
    import assistant.core.config as cfg_mod

    with mock.patch.object(cfg_mod, "CONFIG_FILE", tmp_path / "s.json"), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        _cmd_config(["set", "max_history", "notanumber"])

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert not (tmp_path / "s.json").exists()
