"""Tests for assistant.core.config — Sovereign Core edition."""
import json
import pytest

from assistant.core.config import DEFAULTS, _normalize, load, save


# ---------------------------------------------------------------------------
# _normalize
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_bool_from_string_true(self):
        assert _normalize("true", True) is True
        assert _normalize("True", True) is True
        assert _normalize("1", True) is True
        assert _normalize("yes", True) is True

    def test_bool_from_string_false(self):
        assert _normalize("false", False) is False
        assert _normalize("False", False) is False
        assert _normalize("0", False) is False
        assert _normalize("no", False) is False

    def test_bool_from_int(self):
        assert _normalize(1, True) is True
        assert _normalize(0, False) is False

    def test_bool_passthrough(self):
        assert _normalize(True, True) is True
        assert _normalize(False, False) is False

    def test_int_from_string(self):
        assert _normalize("42", 0) == 42
        assert isinstance(_normalize("42", 0), int)

    def test_int_bad_string_passthrough(self):
        result = _normalize("not_a_number", 0)
        assert result == "not_a_number"

    def test_float_from_string(self):
        result = _normalize("3.14", 1.0)
        assert abs(result - 3.14) < 1e-9

    def test_str_passthrough(self):
        assert _normalize("sovereign", "ollama") == "sovereign"

    def test_unknown_type_passthrough(self):
        assert _normalize([1, 2], []) == [1, 2]


# ---------------------------------------------------------------------------
# DEFAULTS content
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_sovereign_backend_is_default(self):
        assert DEFAULTS["backend"] == "sovereign"

    def test_sovereign_keys_present(self):
        assert "sovereign_url" in DEFAULTS
        assert "sovereign_model" in DEFAULTS

    def test_ollama_keys_present(self):
        assert "ollama_url" in DEFAULTS
        assert "ollama_model" in DEFAULTS

    def test_no_cloud_api_keys(self):
        """Cloud API keys must NOT exist in Sovereign Core edition."""
        cloud_keys = {
            "openai_api_key", "anthropic_api_key", "anthropic_model",
            "mistral_api_key", "mistral_model", "groq_api_key", "groq_model",
        }
        for key in cloud_keys:
            assert key not in DEFAULTS, f"Cloud key '{key}' should not be in DEFAULTS"

    def test_auto_run_bash_default_false(self):
        assert DEFAULTS["auto_run_bash"] is False

    def test_stream_default_true(self):
        assert DEFAULTS["stream"] is True

    def test_timeout_present(self):
        assert "timeout" in DEFAULTS
        assert isinstance(DEFAULTS["timeout"], int)


# ---------------------------------------------------------------------------
# load / save round-trip
# ---------------------------------------------------------------------------

class TestLoadSave:
    def test_load_returns_defaults_when_no_file(self, tmp_path, monkeypatch):
        import assistant.utils.paths as paths
        monkeypatch.setattr(paths, "CONFIG_FILE", tmp_path / "settings.json")
        monkeypatch.setattr(paths, "HISTORY_FILE", tmp_path / "history.db")
        cfg = load()
        assert cfg["backend"] == DEFAULTS["backend"]

    def test_load_merges_user_settings(self, tmp_path, monkeypatch):
        import assistant.utils.paths as paths
        cfg_file = tmp_path / "settings.json"
        cfg_file.write_text(json.dumps({"backend": "ollama", "max_history": 5}))
        monkeypatch.setattr(paths, "CONFIG_FILE", cfg_file)
        monkeypatch.setattr(paths, "HISTORY_FILE", tmp_path / "history.db")
        cfg = load()
        assert cfg["backend"] == "ollama"
        assert cfg["max_history"] == 5
        # All other defaults still present
        assert "sovereign_url" in cfg

    def test_save_and_load_round_trip(self, tmp_path, monkeypatch):
        import assistant.utils.paths as paths
        cfg_file = tmp_path / "settings.json"
        monkeypatch.setattr(paths, "CONFIG_FILE", cfg_file)
        monkeypatch.setattr(paths, "HISTORY_FILE", tmp_path / "history.db")
        settings = load()
        settings["sovereign_url"] = "http://192.168.1.100:8001"
        save(settings)
        reloaded = load()
        assert reloaded["sovereign_url"] == "http://192.168.1.100:8001"

    def test_load_normalizes_string_bool(self, tmp_path, monkeypatch):
        import assistant.utils.paths as paths
        cfg_file = tmp_path / "settings.json"
        cfg_file.write_text(json.dumps({"stream": "true", "auto_run_bash": "false"}))
        monkeypatch.setattr(paths, "CONFIG_FILE", cfg_file)
        monkeypatch.setattr(paths, "HISTORY_FILE", tmp_path / "history.db")
        cfg = load()
        assert cfg["stream"] is True
        assert cfg["auto_run_bash"] is False

    def test_load_normalizes_string_int(self, tmp_path, monkeypatch):
        import assistant.utils.paths as paths
        cfg_file = tmp_path / "settings.json"
        cfg_file.write_text(json.dumps({"max_history": "10", "timeout": "30"}))
        monkeypatch.setattr(paths, "CONFIG_FILE", cfg_file)
        monkeypatch.setattr(paths, "HISTORY_FILE", tmp_path / "history.db")
        cfg = load()
        assert cfg["max_history"] == 10
        assert isinstance(cfg["max_history"], int)
        assert cfg["timeout"] == 30

    def test_load_handles_corrupt_json(self, tmp_path, monkeypatch):
        import assistant.utils.paths as paths
        cfg_file = tmp_path / "settings.json"
        cfg_file.write_text("{not valid json}")
        monkeypatch.setattr(paths, "CONFIG_FILE", cfg_file)
        monkeypatch.setattr(paths, "HISTORY_FILE", tmp_path / "history.db")
        cfg = load()
        assert cfg["backend"] == DEFAULTS["backend"]
