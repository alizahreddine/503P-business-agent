import logging

import pytest

from src.intent import (
    FEEDBACK_UNKNOWN,
    GENERAL_QUESTION,
    LEAD_COLLECTION,
    classify_intent,
    validate_intent,
)


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("What courses do you teach?", GENERAL_QUESTION),
        ("I want to join EECE 210.", LEAD_COLLECTION),
        ("I have a complaint about tutoring.", FEEDBACK_UNKNOWN),
        ("Who teaches EECE 230?", GENERAL_QUESTION),
        ("I want to join, but also report an issue.", LEAD_COLLECTION),
    ],
)
def test_required_academy_examples(message, expected):
    assert classify_intent(message, []) == expected


def test_incomplete_lead_stays_in_lead_collection_on_later_turn():
    history = [
        {"role": "assistant", "content": "What is your name and email?"},
        {"role": "user", "content": "I want to join EECE 210."},
    ]

    assert classify_intent("My name is Sam.", history) == LEAD_COLLECTION
    assert classify_intent("sam@example.com", history) == LEAD_COLLECTION


def test_feedback_unknown_without_lead_context():
    assert classify_intent("I do not know who teaches this.", []) == FEEDBACK_UNKNOWN


def test_empty_or_non_text_input_routes_to_feedback_unknown():
    assert classify_intent("", []) == FEEDBACK_UNKNOWN
    assert classify_intent(None, []) == FEEDBACK_UNKNOWN


def test_classifier_logs_selected_intent(caplog):
    with caplog.at_level(logging.INFO, logger="src.intent"):
        result = classify_intent("What courses do you teach?", [])

    assert result == GENERAL_QUESTION
    assert "Selected intent=GENERAL_QUESTION" in caplog.text


def test_intent_validation_rejects_unexpected_categories():
    assert validate_intent(GENERAL_QUESTION) == GENERAL_QUESTION
    with pytest.raises(ValueError, match="Invalid intent"):
        validate_intent("REGISTRATION")
