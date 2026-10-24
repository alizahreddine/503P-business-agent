"""Opt-in live tests; skipped unless explicitly enabled with a real API key."""

import os

import pytest
from dotenv import dotenv_values

from src.config import load_settings
from src.llm_client import OpenAIStudentConcierge, load_business_knowledge


HAS_OPENAI_API_KEY = bool(
    os.getenv("OPENAI_API_KEY") or dotenv_values(".env").get("OPENAI_API_KEY")
)


pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_LIVE_LLM_TESTS") or not HAS_OPENAI_API_KEY,
    reason="Set RUN_LIVE_LLM_TESTS=1 and OPENAI_API_KEY to run live tests.",
)


def test_live_openai_smoke():
    agent = OpenAIStudentConcierge()
    result = agent.chat(
        system_prompt="Answer briefly and do not invent availability.",
        business_knowledge=load_business_knowledge(),
        history=[],
        user_message="What is The A Way?",
    )
    assert result.success is True
    assert result.text
