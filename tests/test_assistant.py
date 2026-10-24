from pathlib import Path
import sqlite3

from src.assistant import StudentConcierge
from src.config import Settings
from src.llm_client import LLMResult


class FakeModel:
    def __init__(self):
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)
        return LLMResult(success=True, text="General answer from the academy.")


def test_multi_turn_lead_collects_slots_without_repeating_course(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))
    assistant = StudentConcierge(
        client=FakeModel(),
        business_knowledge="Catalog context",
        max_history_messages=12,
    )

    assert "name" in assistant.respond("s1", "I want EECE 210.").lower()
    assert "email" in assistant.respond("s1", "Sam Student").lower()
    final = assistant.respond("s1", "sam@example.com")

    assert "recorded" in final.lower()
    assert "enrollment" in final.lower()
    assert assistant.respond("s1", "Can you confirm?") == (
        "Your interest was already recorded for follow-up. This does not confirm "
        "enrollment or registration."
    )
    assert assistant.client.calls == []
    with sqlite3.connect(tmp_path / "customer_records.sqlite3") as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM customer_interest"
        ).fetchone()[0] == 1


def test_session_separation_and_reset(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))
    model = FakeModel()
    assistant = StudentConcierge(client=model, business_knowledge="Context")

    assert "name" in assistant.respond("one", "I want EECE 210.").lower()
    second_reply = assistant.respond("two", "I want CMPS 203.")
    assert "name" in second_reply.lower()
    assert len(assistant.get_history("one")) == 2
    assert len(assistant.get_history("two")) == 2
    assistant.reset("one")
    assert assistant.get_history("one") == []
    assert assistant.respond("one", "My name is New Student.") == (
        "General answer from the academy."
    )


def test_partial_information_does_not_write_success(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))
    assistant = StudentConcierge(client=FakeModel(), business_knowledge="Context")

    assistant.respond("s1", "I want EECE 210.")
    assistant.respond("s1", "Sam Student")

    assert not (tmp_path / "customer_records.sqlite3").exists()


def test_mixed_intent_stays_lead_and_preserves_issue(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))
    assistant = StudentConcierge(client=FakeModel(), business_knowledge="Context")

    first = assistant.respond("s1", "I want EECE 210, but I also have an issue.")
    assert "name" in first.lower()
    assistant.respond("s1", "Sam")
    final = assistant.respond("s1", "sam@example.com")

    assert "recorded" in final.lower()
    assert assistant.client.calls == []


def test_finite_turn_limit_stops_session(tmp_path):
    assistant = StudentConcierge(
        client=FakeModel(), business_knowledge="Context", max_turns=1
    )

    assistant.respond("s1", "What courses do you teach?")
    assert "safety limit" in assistant.respond("s1", "And EECE 210?").lower()


def test_general_question_uses_model_and_keeps_session_history(tmp_path):
    model = FakeModel()
    assistant = StudentConcierge(client=model, business_knowledge="Context")

    assert assistant.respond("s1", "What courses do you teach?") == (
        "General answer from the academy."
    )
    assert len(model.calls) == 1
    assert model.calls[0]["history"] == []
    assert assistant.get_history("s1")[0]["content"] == "What courses do you teach?"


def test_payment_and_official_registration_request_is_refused_without_model(tmp_path):
    model = FakeModel()
    assistant = StudentConcierge(client=model, business_knowledge="Context")

    reply = assistant.respond("s1", "Register me now and take my payment.")

    assert "cannot process payments" in reply.lower()
    assert model.calls == []
