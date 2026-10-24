"""Session-scoped multi-turn orchestration for The A Way Student Concierge."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from src.identity import build_system_prompt
from src.intent import FEEDBACK_UNKNOWN, LEAD_COLLECTION, classify_intent
from src.llm_client import LLMResult, OpenAIStudentConcierge, load_business_knowledge
from src.tools import record_customer_interest

logger = logging.getLogger(__name__)

_EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)+\b", re.I
)
_COURSE_PATTERN = re.compile(r"\b(?:EECE|CMPS)\s?\d{3}\b", re.I)
_NAME_PATTERN = re.compile(
    r"\b(?:my name is|i am|i'm|name:)\s+([A-Za-z][A-Za-z .'-]{1,60})",
    re.I,
)


@dataclass
class SessionState:
    """Conversation and lead state belonging to one session ID."""

    history: list[dict[str, str]] = field(default_factory=list)
    lead_course: str | None = None
    lead_name: str | None = None
    lead_email: str | None = None
    lead_notes: list[str] = field(default_factory=list)
    lead_recorded: bool = False
    turn_count: int = 0


class StudentConcierge:
    """Coordinate bounded, independent conversations by session."""

    def __init__(
        self,
        *,
        client: OpenAIStudentConcierge | None = None,
        business_knowledge: str | None = None,
        max_history_messages: int = 12,
        max_turns: int = 20,
    ) -> None:
        if max_history_messages < 2:
            raise ValueError("max_history_messages must be at least 2.")
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1.")
        self.client = client or OpenAIStudentConcierge()
        self.business_knowledge = business_knowledge or load_business_knowledge()
        self.max_history_messages = max_history_messages
        self.max_turns = max_turns
        self._sessions: dict[str, SessionState] = {}

    def respond(self, session_id: str, message: str) -> str:
        """Handle one turn and return only the user-facing assistant text."""

        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be nonempty.")
        if not isinstance(message, str) or not message.strip():
            return "Please send a question or message so I can help."
        state = self._sessions.setdefault(session_id, SessionState())
        if state.turn_count >= self.max_turns:
            return "This conversation has reached its safety limit. Please start a new session."
        state.turn_count += 1
        if state.lead_recorded and re.search(
            r"\b(?:confirm|registered|registration|enrolled|enrollment)\b",
            message,
            re.I,
        ):
            reply = (
                "Your interest was already recorded for follow-up. This does not "
                "confirm enrollment or registration."
            )
            state.history.extend(
                [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
            )
            state.history = state.history[-self.max_history_messages :]
            return reply
        if len(state.history) >= self.max_history_messages:
            state.history = state.history[-(self.max_history_messages - 2) :]

        intent = classify_intent(message, state.history)
        boundary_reply = _out_of_scope_reply(message)
        if boundary_reply:
            reply = boundary_reply
        elif intent == LEAD_COLLECTION or self._lead_in_progress(state):
            reply = self._handle_lead(state, message)
        else:
            try:
                result = self.client.chat(
                    system_prompt=(
                        build_system_prompt()
                        + "\n\nROUTER RESULT:\n"
                        + _routing_instruction(intent)
                    ),
                    business_knowledge=self.business_knowledge,
                    history=list(state.history),
                    user_message=message,
                )
                reply = self._model_reply(result, intent)
            except (RuntimeError, ValueError, TypeError) as exc:
                logger.warning("Assistant model request failed: %s", exc)
                reply = (
                    "I’m sorry, I could not complete that request right now. "
                    "Please try again."
                )

        state.history.extend(
            [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
        )
        state.history = state.history[-self.max_history_messages :]
        logger.info("session=%s intent=%s", session_id, intent)
        return reply

    def reset(self, session_id: str) -> None:
        """Remove all history and lead slots for a session."""

        self._sessions.pop(session_id, None)
        logger.info("session reset=%s", session_id)

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        """Return a copy of one session's bounded history."""

        state = self._sessions.get(session_id)
        return list(state.history) if state else []

    def _handle_lead(self, state: SessionState, message: str) -> str:
        if state.lead_recorded:
            return (
                "Your interest was already recorded for follow-up. This does not "
                "confirm enrollment or registration."
            )
        course = _extract_course(message)
        if course and state.lead_course is None:
            state.lead_course = course
        name = _extract_name(message)
        if name and state.lead_name is None:
            state.lead_name = name
        email = _extract_email(message)
        if email and state.lead_email is None:
            state.lead_email = email

        mixed_issue = bool(re.search(r"\b(?:issue|complaint|feedback|problem)\b", message, re.I))
        if not _is_slot_value(message, state) or mixed_issue:
            state.lead_notes.append(message.strip())

        if not state.lead_course:
            return "Which course are you interested in?"
        if not state.lead_name:
            return "What name should I use for your interest request?"
        if not state.lead_email:
            return "What email address should we use for follow-up?"

        notes = " ".join(state.lead_notes + [f"Interest in {state.lead_course}."]).strip()
        result = record_customer_interest(state.lead_email, state.lead_name, notes)
        if not result.get("success"):
            return (
                "I could not record the interest request yet: "
                f"{result.get('error', 'validation failed')}"
            )
        state.lead_recorded = True
        return (
            "Your interest was recorded for follow-up. This does not confirm "
            "enrollment or registration."
        )

    def _lead_in_progress(self, state: SessionState) -> bool:
        return bool(
            (state.lead_course or state.lead_name or state.lead_email)
            and not state.lead_recorded
        )

    @staticmethod
    def _model_reply(result: LLMResult, intent: str) -> str:
        if result.success and result.text:
            return result.text
        if intent == FEEDBACK_UNKNOWN:
            return "I could not complete the feedback request right now. Please try again."
        return "I could not complete that request right now. Please try again."


def _extract_course(message: str) -> str | None:
    match = _COURSE_PATTERN.search(message)
    return match.group(0).upper().replace(" ", " ") if match else None


def _extract_email(message: str) -> str | None:
    match = _EMAIL_PATTERN.search(message)
    return match.group(0).lower() if match else None


def _extract_name(message: str) -> str | None:
    match = _NAME_PATTERN.search(message)
    if match:
        return match.group(1).strip(" .,'")
    if (
        not _extract_email(message)
        and not _extract_course(message)
        and len(message.split()) <= 4
        and re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,60}", message.strip())
    ):
        return message.strip()
    return None


def _is_slot_value(message: str, state: SessionState) -> bool:
    return bool(
        _extract_email(message)
        or _extract_course(message)
        or (_extract_name(message) and not state.lead_name)
    )


def _routing_instruction(intent: str) -> str:
    """Turn the deterministic router decision into an explicit model directive."""

    if intent == FEEDBACK_UNKNOWN:
        return (
            f"Selected intent: {FEEDBACK_UNKNOWN}. Call record_feedback with the "
            "student's message before replying. Do not claim it was logged unless "
            "the tool result reports success."
        )
    return (
        f"Selected intent: {intent}. Answer only from the supplied business "
        "knowledge. If the answer is not documented, call record_feedback with "
        "the unanswered question before replying."
    )


def _out_of_scope_reply(message: str) -> str | None:
    """Return a safe response for administrative actions the agent cannot take."""

    if re.search(
        r"\b(?:payment|pay(?:ment)?|credit card|bank|balance|invoice)\b",
        message,
        re.I,
    ):
        return (
            "I cannot process payments or access financial records. I can answer "
            "documented questions or record course interest for academy follow-up."
        )
    if re.search(
        r"\b(?:admin(?:istrator)? records?|admin database|dashboard|student portal|"
        r"tutor portal|private student records?)\b",
        message,
        re.I,
    ):
        return (
            "I cannot access administrator records, dashboards, or student/tutor "
            "portals. I can help only with documented public academy information."
        )
    if re.search(
        r"\b(?:officially (?:register|enroll)|(?:register|enroll) me now|"
        r"complete (?:my )?(?:registration|enrollment))\b",
        message,
        re.I,
    ):
        return (
            "I cannot complete official registration or enrollment. I can record "
            "your course interest for academy follow-up, which is not confirmation."
        )
    return None
