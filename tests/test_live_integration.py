"""Opt-in real OpenAI integration tests.

These tests are never part of ordinary deterministic unit-test runs.
"""

import os

import pytest
from dotenv import dotenv_values

from src.llm_client import OpenAIStudentConcierge, load_business_knowledge


HAS_OPENAI_API_KEY = bool(
    os.getenv("OPENAI_API_KEY") or dotenv_values(".env").get("OPENAI_API_KEY")
)


pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_LIVE_LLM_TESTS") or not HAS_OPENAI_API_KEY,
    reason="Set RUN_LIVE_LLM_TESTS=1 and OPENAI_API_KEY to run live integration tests.",
)


def test_live_text_response():
    result = OpenAIStudentConcierge().chat(
        system_prompt="Answer briefly and do not invent availability.",
        business_knowledge=load_business_knowledge(),
        history=[],
        user_message="What is The A Way?",
    )
    assert result.success is True
    assert result.text


def test_live_tool_call_cycle():
    result = OpenAIStudentConcierge().chat(
        system_prompt=(
            "If the student asks an unanswered business question, call "
            "record_feedback before replying."
        ),
        business_knowledge=load_business_knowledge(),
        history=[],
        user_message="Who teaches the unconfirmed Saturday EECE 230 section?",
    )
    assert result.success is True
    assert result.text
    assert any(call["name"] == "record_feedback" for call in result.tool_calls)
