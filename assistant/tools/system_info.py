"""
System information tool — Termux/Android context for the AI.

Provides a compact device summary injected into the system prompt so the AI
gives device-aware answers (architecture, available RAM, storage, Termux paths).
"""
from __future__ import annotations

import platform
import subprocess
import os


def _run(cmd: str) -> str:
    """Run a shell command and return stdout, empty string on failure."""
    try:
        result = subprocess.run(
            cmd, shell=True, text=True, capture_output=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_context() -> str:
    """Return a compact system context string for the system prompt."""
    lines: list[str] = ["System context:"]

    # OS / kernel
    system = platform.system()
    machine = platform.machine()
    release = platform.release()
    lines.append(f"  OS: {system} {release} ({machine})")

    # Termux detection
    termux_prefix = os.environ.get("PREFIX", "")
    if "termux" in termux_prefix.lower() or "/com.termux" in termux_prefix:
        lines.append("  Environment: Termux (Android)")
        # Android version
        av = _run("getprop ro.build.version.release")
        if av:
            lines.append(f"  Android: {av}")
    else:
        lines.append(f"  Environment: Linux terminal")

    # CPU
    cpu_info = _run("cat /proc/cpuinfo 2>/dev/null | grep 'Hardware\\|Model name' | head -1")
    if not cpu_info:
        cpu_info = platform.processor() or machine
    if cpu_info:
        lines.append(f"  CPU: {cpu_info.split(':')[-1].strip()}")

    # RAM
    mem = _run("free -m 2>/dev/null | awk '/^Mem/{print $2\" MB total, \"$7\" MB available\"}'")
    if mem:
        lines.append(f"  RAM: {mem}")

    # Storage
    storage = _run("df -h / 2>/dev/null | awk 'NR==2{print $4\" free of \"$2}'")
    if storage:
        lines.append(f"  Storage: {storage}")

    # Python
    py = f"{platform.python_version()} ({machine})"
    lines.append(f"  Python: {py}")

    # Shell
    shell = os.environ.get("SHELL", _run("echo $SHELL") or "unknown")
    lines.append(f"  Shell: {shell}")

    return "\n".join(lines)
