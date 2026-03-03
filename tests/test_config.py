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
