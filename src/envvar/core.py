"""Utilities for loading and validating environment variables."""

import os
from typing import Final

from dotenv import find_dotenv, load_dotenv

_ENV_LOADED = False


def _ensure_env_loaded(*, usecwd: bool = True) -> None:
    """Load a ``.env`` file once so environment lookups succeed."""
    global _ENV_LOADED  # cache flag guarding repeated loads
    if _ENV_LOADED:
        return

    path: str | None = find_dotenv(usecwd=usecwd)
    if path:
        load_dotenv(dotenv_path=path)

    _ENV_LOADED = True


def get_env(name: str) -> str:
    """Return a required environment variable value or raise an error."""
    _ensure_env_loaded()

    value = os.getenv(name, "").strip()
    if not value:
        msg: Final[str] = (
            f"Configure the environment variable '{name}' before running the app."
        )
        raise RuntimeError(msg)
    return value
