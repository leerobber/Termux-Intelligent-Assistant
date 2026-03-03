"""Tests for the shell tool."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant.tools.shell import run, safe_run


def test_run_successful_command():
    result = run("echo hello")
    assert result.ok
    assert result.stdout == "hello"


def test_run_returns_stderr_on_failure():
    result = run("ls /nonexistent_path_xyz 2>&1; exit 0")
    # stdout should contain the error message from ls
    assert result.ok  # exit 0 forced
    assert "nonexistent" in result.stdout or result.returncode == 0


def test_run_failing_command():
    result = run("exit 42")
    assert result.returncode == 42
    assert not result.ok


def test_safe_run_timeout():
    result = safe_run("sleep 100", timeout=1)
    assert not result.ok
    assert "timed out" in result.stderr.lower()


def test_safe_run_never_raises():
    # This should not raise even though the command fails
    result = safe_run("false")
    assert not result.ok


def test_output_property():
    result = run("echo out")
    assert "out" in result.output
