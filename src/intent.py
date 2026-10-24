"""Deterministic, API-free intent classification for the student concierge."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any

GENERAL_QUESTION = "GENERAL_QUESTION"
LEAD_COLLECTION = "LEAD_COLLECTION"
FEEDBACK_UNKNOWN = "FEEDBACK_UNKNOWN"
VALID_INTENTS = frozenset(
    {GENERAL_QUESTION, LEAD_COLLECTION, FEEDBACK_UNKNOWN}
)

logger = logging.getLogger(__name__)

_LEAD_PATTERNS = (
    r"\b(?:want|would like|interested|interest|sign me|join|enroll|register)\b",
    r"\b(?:contact|reach out|follow up|follow-up)\b",
)
_FEEDBACK_PATTERNS = (
    r"\b(?:complaint|complain|issue|problem|feedback|unhappy|bad experience)\b",
    r"\b(?:don't know|do not know|unknown|not sure|unanswered)\b",
)
_LEAD_FOLLOW_UP_PATTERNS = (
    r"\b(?:my name is|i am|i'm|my email|you can reach me)\b",
    r"\b(?:here are my details|contact details)\b",
)


def validate_intent(intent: str) -> str:
    """Return a valid intent or raise a clear error for invalid classifier output."""

    if intent not in VALID_INTENTS:
        raise ValueError(
            f"Invalid intent {intent!r}; expected one of "
            f"{', '.join(sorted(VALID_INTENTS))}."
        )
    return intent


def classify_intent(message: str, history: Sequence[Any] | None = None) -> str:
    """Classify a message into exactly one supported primary intent.

    Rationale: deterministic heuristics keep ordinary tests offline and make the
    routing policy inspectable. Lead signals have priority over feedback in a
    mixed request because preserving an incomplete lead conversation is the
    least disruptive continuation; the issue remains in the lead notes for the
    later handler. Feedback/unknown signals precede general questions. A prior
    lead context plus contact-detail follow-up remains lead collection.
    """

    if not isinstance(message, str) or not message.strip():
        selected = FEEDBACK_UNKNOWN
    else:
        normalized = message.casefold()
        lead_signal = _matches(normalized, _LEAD_PATTERNS)
        feedback_signal = _matches(normalized, _FEEDBACK_PATTERNS)
        continuing_lead = _lead_context(history) and (
            _matches(normalized, _LEAD_FOLLOW_UP_PATTERNS)
            or _looks_like_contact_detail(normalized)
        )

        if lead_signal or continuing_lead:
            selected = LEAD_COLLECTION
        elif feedback_signal:
            selected = FEEDBACK_UNKNOWN
        else:
            selected = GENERAL_QUESTION

    selected = validate_intent(selected)
    logger.info("Selected intent=%s message=%r", selected, message)
    return selected


def _matches(message: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, message) for pattern in patterns)


def _looks_like_contact_detail(message: str) -> bool:
    return bool(re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", message, re.I))


def _lead_context(history: Sequence[Any] | None) -> bool:
    if not history:
        return False
    for item in history:
        text = _history_text(item).casefold()
        if "lead_collection" in text or "lead collection" in text:
            return True
        if "name and email" in text or "contact details" in text:
            return True
    return False


def _history_text(item: Any) -> str:
    if isinstance(item, Mapping):
        return str(item.get("content", ""))
    if isinstance(item, (tuple, list)) and len(item) >= 2:
        return str(item[1])
    return str(item)
