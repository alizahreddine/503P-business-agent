from pathlib import Path

from app import create_app
from src.config import Settings, load_settings

import pytest


def test_settings_load_without_api_key(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("THE_A_WAY_MAX_HISTORY_MESSAGES", "4")

    settings = load_settings(
        env_file=tmp_path / "intentionally-missing.env",
        data_dir=tmp_path,
    )

    assert settings.openai_api_key is None
    assert settings.openai_model == "test-model"
    assert settings.data_dir == tmp_path
    assert settings.max_history_messages == 4
    assert settings.has_api_key is False


def test_settings_reject_invalid_history_limit(monkeypatch):
    monkeypatch.setenv("THE_A_WAY_MAX_HISTORY_MESSAGES", "zero")

    try:
        load_settings()
    except ValueError as exc:
        assert "must be an integer" in str(exc)
    else:
        raise AssertionError("Expected invalid history limit to raise ValueError")


def test_settings_reject_history_limit_too_small(monkeypatch):
    monkeypatch.setenv("THE_A_WAY_MAX_HISTORY_MESSAGES", "1")

    with pytest.raises(ValueError, match="at least 2"):
        load_settings()


def test_app_uses_the_supplied_runtime_settings(tmp_path):
    supplied = Settings("test-key", "test-model", tmp_path, 4)

    assistant = create_app(supplied)

    assert assistant.max_history_messages == 4
    assert assistant.client.settings is supplied
    assert "BUSINESS PROFILE PDF" in assistant.business_knowledge


def test_settings_repr_never_contains_api_key(tmp_path):
    settings = Settings("sensitive-test-value", "test-model", tmp_path, 4)

    assert "sensitive-test-value" not in repr(settings)
    assert "openai_api_key" not in repr(settings)
