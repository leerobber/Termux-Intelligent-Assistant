"""Tests for the configuration loader."""
import json
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import assistant.core.config as cfg_mod  # noqa: E402  (after sys.path patch)


def test_load_returns_defaults_when_no_file(tmp_path):
    """load() must return defaults when config file is absent."""
    with mock.patch.object(cfg_mod, "CONFIG_FILE", tmp_path / "missing.json"), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        settings = cfg_mod.load()

    assert settings["backend"] == "ollama"
    assert settings["max_history"] == 20


def test_load_merges_user_overrides(tmp_path):
    """User values in settings.json override the defaults."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"backend": "openai", "max_history": 5}))

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        settings = cfg_mod.load()

    assert settings["backend"] == "openai"
    assert settings["max_history"] == 5
    # Default for unset keys should still be present
    assert "ollama_model" in settings


def test_anthropic_defaults_present(tmp_path):
    """anthropic_model, anthropic_api_key, and anthropic_max_tokens must exist in defaults."""
    with mock.patch.object(cfg_mod, "CONFIG_FILE", tmp_path / "missing.json"), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        settings = cfg_mod.load()

    assert "anthropic_model" in settings
    assert settings["anthropic_model"] == "claude-3-5-sonnet-20241022"
    assert "anthropic_api_key" in settings
    assert settings["anthropic_api_key"] == ""
    assert "anthropic_max_tokens" in settings
    assert settings["anthropic_max_tokens"] == 4096


def test_anthropic_defaults_survive_merge(tmp_path):
    """anthropic_* defaults are still present when user overrides other keys."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"backend": "anthropic"}))

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        settings = cfg_mod.load()

    assert settings["anthropic_model"] == "claude-3-5-sonnet-20241022"
    assert "anthropic_api_key" in settings
    assert "anthropic_max_tokens" in settings


def test_save_roundtrip(tmp_path):
    """save() + load() round-trip preserves values."""
    settings_file = tmp_path / "settings.json"
    data = {"backend": "openai", "max_history": 10}

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        cfg_mod.save(data)
        loaded = json.loads(settings_file.read_text())

    assert loaded["backend"] == "openai"
    assert loaded["max_history"] == 10


# ---------------------------------------------------------------------------
# _normalize tests
# ---------------------------------------------------------------------------

def test_normalize_string_to_int():
    """_normalize converts a string to int when default is int."""
    assert cfg_mod._normalize("5", 20) == 5
    assert isinstance(cfg_mod._normalize("5", 20), int)


def test_normalize_string_bool_true():
    """_normalize converts truthy string to True when default is bool."""
    for raw in ("true", "True", "1", "yes"):
        assert cfg_mod._normalize(raw, True) is True


def test_normalize_string_bool_false():
    """_normalize converts falsy string to False when default is bool."""
    for raw in ("false", "False", "0", "no"):
        assert cfg_mod._normalize(raw, True) is False


def test_normalize_bool_unchanged():
    """_normalize leaves a correctly-typed bool unchanged."""
    assert cfg_mod._normalize(False, True) is False
    assert cfg_mod._normalize(True, True) is True


def test_normalize_int_for_bool_default():
    """_normalize coerces 0/1 integer to bool when default is bool."""
    assert cfg_mod._normalize(0, True) is False
    assert cfg_mod._normalize(1, True) is True


def test_normalize_invalid_string_for_int_returns_unchanged():
    """_normalize returns original value when string cannot be coerced to int."""
    result = cfg_mod._normalize("notanumber", 20)
    assert result == "notanumber"


def test_normalize_correct_type_unchanged():
    """_normalize returns value as-is when it already matches default type."""
    assert cfg_mod._normalize(42, 20) == 42
    assert cfg_mod._normalize("openai", "ollama") == "openai"


# ---------------------------------------------------------------------------
# load() normalization tests
# ---------------------------------------------------------------------------

def test_load_normalizes_string_int(tmp_path):
    """load() coerces string-typed int values from legacy config files."""
    settings_file = tmp_path / "settings.json"
    # Simulate legacy config with max_history stored as string
    settings_file.write_text(json.dumps({"max_history": "7"}))

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        settings = cfg_mod.load()

    assert settings["max_history"] == 7
    assert isinstance(settings["max_history"], int)


def test_load_normalizes_string_bool(tmp_path):
    """load() coerces string-typed bool values from legacy config files."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"stream": "false"}))

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        settings = cfg_mod.load()

    assert settings["stream"] is False


def test_load_normalizes_string_anthropic_max_tokens(tmp_path):
    """load() coerces string anthropic_max_tokens to int."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"anthropic_max_tokens": "1024"}))

    with mock.patch.object(cfg_mod, "CONFIG_FILE", settings_file), \
         mock.patch.object(cfg_mod, "ensure_data_dir"):
        settings = cfg_mod.load()

    assert settings["anthropic_max_tokens"] == 1024
    assert isinstance(settings["anthropic_max_tokens"], int)
