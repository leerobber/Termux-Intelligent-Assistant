"""
Path utilities using pathlib — all paths are relative to the project root.
No hardcoded absolute paths are used anywhere in this module.
"""
from pathlib import Path

# Project root is two levels above this file: assistant/utils/paths.py -> root
ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_DIR = ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "settings.json"
DATA_DIR = ROOT / "data"
HISTORY_FILE = DATA_DIR / "history.db"
LOG_FILE = DATA_DIR / "assistant.log"


def resolve(relative: str) -> Path:
    """Return an absolute Path for *relative* (relative to project root)."""
    return ROOT / relative


def ensure_data_dir() -> None:
    """Create the data directory if it does not exist yet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
