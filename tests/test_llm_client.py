import json
from types import SimpleNamespace

from src.config import Settings
from src.llm_client import OpenAIStudentConcierge


def _settings(tmp_path):
    return Settings(
        openai_api_key="test-key",
        openai_model="test-model",
        data_dir=tmp_path,
        max_history_messages=12,
    )


class FakeCompletions:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return next(self.responses)


class FakeClient:
    def __init__(self, responses):
        self.completions = FakeCompletions(responses)
        self.chat = SimpleNamespace(completions=self.completions)


def _response(message):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(**message))]
    )


def test_genuine_tool_call_cycle_executes_and_returns_final_reply(monkeypatch, tmp_path):
    first = _response(
        {
            "content": None,
            "tool_calls": [
                SimpleNamespace(
                    id="call-1",
                    type="function",
                    function=SimpleNamespace(
                        name="record_feedback",
                        arguments=json.dumps(
                            {"question": "Who teaches EECE 230?"}
                        ),
                    ),
                )
            ],
        }
    )
    second = _response(
        {
            "content": "I recorded your unanswered question for follow-up.",
            "tool_calls": [],
        }
    )
    fake = FakeClient([first, second])
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))
    agent = OpenAIStudentConcierge(settings=_settings(tmp_path), client=fake)

    result = agent.chat(
        system_prompt="Be helpful.",
        business_knowledge="Catalog only; active offerings are unconfirmed.",
        history=[{"role": "user", "content": "Earlier question"}],
        user_message="Who teaches EECE 230?",
    )

    assert result.success is True
    assert result.text == "I recorded your unanswered question for follow-up."
    assert result.tool_calls[0]["name"] == "record_feedback"
    assert result.tool_results[0]["success"] is True
    assert len(fake.completions.requests) == 2
    second_request = fake.completions.requests[1]["messages"]
    assert any(message["role"] == "tool" for message in second_request)
    assert any(message["role"] == "system" for message in fake.completions.requests[0]["messages"])


def test_text_response_is_returned_without_tool_call(tmp_path):
    fake = FakeClient([_response({"content": "Catalog answer.", "tool_calls": []})])
    agent = OpenAIStudentConcierge(settings=_settings(tmp_path), client=fake)

    result = agent.chat(
        system_prompt="Rules",
        business_knowledge="Knowledge",
        history=[],
        user_message="What courses do you teach?",
    )

    assert result.success is True
    assert result.text == "Catalog answer."
    assert result.tool_calls == []


def test_malformed_tool_arguments_return_failure_without_execution(tmp_path):
    response = _response(
        {
            "content": None,
            "tool_calls": [
                SimpleNamespace(
                    id="call-bad",
                    function=SimpleNamespace(
                        name="record_feedback", arguments="{not-json"
                    ),
                )
            ],
        }
    )
    fake = FakeClient([response])
    agent = OpenAIStudentConcierge(settings=_settings(tmp_path), client=fake)

    result = agent.chat(
        system_prompt="Rules",
        business_knowledge="Knowledge",
        history=[],
        user_message="Unknown question",
    )

    assert result.success is False
    assert "valid JSON" in result.error


def test_missing_key_is_reported_without_constructing_provider(tmp_path):
    settings = Settings(
        openai_api_key=None,
        openai_model="test-model",
        data_dir=tmp_path,
        max_history_messages=12,
    )
    agent = OpenAIStudentConcierge(settings=settings)

    try:
        agent.client
    except RuntimeError as exc:
        assert "OPENAI_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected missing API key failure")
