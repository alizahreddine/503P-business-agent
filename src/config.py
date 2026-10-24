"""Environment-backed configuration for the future business agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    openai_api_key: str | None = field(repr=False)
    openai_model: str
    data_dir: Path
    max_history_messages: int

    @property
    def has_api_key(self) -> bool:
        """Return whether a non-empty API key is configured."""

        return bool(self.openai_api_key)


def load_settings(
    env_file: str | Path | None = None,
    *,
    data_dir: str | Path | None = None,
) -> Settings:
    """Load settings without requiring an API key.

    ``env_file`` is optional so imports and tests work in environments without a
    local .env file. Explicit environment variables take precedence.
    """

    if env_file is not None:
        load_dotenv(dotenv_path=env_file, override=False)
    else:
        load_dotenv(override=False)

    raw_limit = os.getenv("THE_A_WAY_MAX_HISTORY_MESSAGES", "12")
    try:
        max_history_messages = int(raw_limit)
    except ValueError as exc:
        raise ValueError(
            "THE_A_WAY_MAX_HISTORY_MESSAGES must be an integer."
        ) from exc
    if max_history_messages < 2:
        raise ValueError("THE_A_WAY_MAX_HISTORY_MESSAGES must be at least 2.")

    resolved_data_dir = Path(
        data_dir if data_dir is not None else os.getenv("THE_A_WAY_DATA_DIR", "data")
    )
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        data_dir=resolved_data_dir,
        max_history_messages=max_history_messages,
    )
