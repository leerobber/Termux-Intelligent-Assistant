"""Tests for path utilities — verifies no hardcoded absolute paths are used."""
import sys
from pathlib import Path

# Allow running from project root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant.utils.paths import (
    CONFIG_DIR,
    CONFIG_FILE,
    DATA_DIR,
    HISTORY_FILE,
    LOG_FILE,
    ROOT,
    resolve,
)


def test_root_is_absolute():
    assert ROOT.is_absolute()


def test_derived_paths_are_under_root():
    for p in (CONFIG_DIR, CONFIG_FILE, DATA_DIR, HISTORY_FILE, LOG_FILE):
        assert str(p).startswith(str(ROOT)), f"{p} is not under ROOT"


def test_resolve_returns_absolute():
    p = resolve("some/relative/file.txt")
    assert p.is_absolute()
    assert str(p).startswith(str(ROOT))


def test_no_hardcoded_paths_in_sources():
    """Scan Python source files for hardcoded /data/data or /home/<user> paths."""
    src_root = ROOT / "assistant"
    bad_prefixes = ("/data/data/com.termux", "/home/")
    violations: list[str] = []
    for py_file in src_root.rglob("*.py"):
        text = py_file.read_text()
        for prefix in bad_prefixes:
            if prefix in text:
                violations.append(f"{py_file}: contains '{prefix}'")
    assert not violations, "Hardcoded paths found:\n" + "\n".join(violations)
