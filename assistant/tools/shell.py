"""
Shell command execution tool.

Runs Termux / Linux shell commands safely inside a subprocess and returns
the combined stdout + stderr.  Designed to be as lightweight as possible.
"""
import shlex
import subprocess
from typing import NamedTuple


class CmdResult(NamedTuple):
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def output(self) -> str:
        """Combined output for display."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)


def run(command: str, timeout: int = 30) -> CmdResult:
    """
    Execute *command* in the system shell and return a CmdResult.

    The command is passed to the shell so pipes, redirects, etc. work.
    Raises subprocess.TimeoutExpired if *timeout* seconds elapse.
    """
    proc = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return CmdResult(
        returncode=proc.returncode,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
    )


def safe_run(command: str, timeout: int = 30) -> CmdResult:
    """
    Like *run* but never raises — returns a failed CmdResult on error.
    Suitable for untrusted / agent-generated commands.
    """
    try:
        return run(command, timeout=timeout)
    except subprocess.TimeoutExpired:
        return CmdResult(-1, "", f"Command timed out after {timeout}s: {command}")
    except Exception as exc:  # noqa: BLE001
        return CmdResult(-1, "", str(exc))
