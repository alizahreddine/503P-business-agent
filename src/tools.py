"""Persistent tool functions exposed to the future model adapter."""

from __future__ import annotations

import hashlib
import logging
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import load_settings

logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"^[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)+$", re.I)
COURSE_INTEREST_PATTERN = re.compile(
    r"\b(?:EECE|CMPS)\s?\d{3}\b|\b(?:course|class|tutor(?:ing)?|subject)\b",
    re.I,
)

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "record_customer_interest",
            "description": (
                "Record a prospective student's interest for academy follow-up. "
                "This does not enroll or register the student."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Prospective student's email address.",
                    },
                    "name": {
                        "type": "string",
                        "description": "Prospective student's name.",
                    },
                    "message": {
                        "type": "string",
                        "description": (
                            "Nonempty course interest or follow-up message; include "
                            "the course the student is interested in when known."
                        ),
                    },
                },
                "required": ["email", "name", "message"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_feedback",
            "description": (
                "Save meaningful student feedback or an unanswered question for "
                "follow-up."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Meaningful feedback or unanswered question.",
                    }
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
]


def record_customer_interest(email: str, name: str, message: str) -> dict[str, Any]:
    """Validate and persist one idempotent customer-interest record."""

    email_value = email.strip().lower() if isinstance(email, str) else ""
    name_value = name.strip() if isinstance(name, str) else ""
    message_value = message.strip() if isinstance(message, str) else ""
    if not EMAIL_PATTERN.fullmatch(email_value):
        return _failure("email must be a valid email address")
    if not name_value:
        return _failure("name must be nonempty")
    if not message_value or not COURSE_INTEREST_PATTERN.search(message_value):
        return _failure("message must be nonempty and include course interest")

    fingerprint = _fingerprint("interest", email_value, name_value, message_value)
    created_at = _utc_now()
    try:
        with _connect() as connection:
            _initialize_schema(connection)
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO customer_interest
                    (fingerprint, email, name, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (fingerprint, email_value, name_value, message_value, created_at),
            )
            row = connection.execute(
                """
                SELECT id, created_at FROM customer_interest
                WHERE fingerprint = ?
                """,
                (fingerprint,),
            ).fetchone()
        if row is None:
            return _failure("interest record could not be persisted")
        duplicate = cursor.rowcount == 0
        logger.info(
            "record_customer_interest persisted id=%s duplicate=%s", row["id"], duplicate
        )
        return {
            "success": True,
            "record_type": "customer_interest",
            "record_id": row["id"],
            "created_at": row["created_at"],
            "duplicate": duplicate,
            "message": "Customer interest recorded for follow-up.",
        }
    except sqlite3.Error:
        logger.exception("Failed to persist customer interest")
        return _failure("customer interest could not be persisted")


def record_feedback(question: str) -> dict[str, Any]:
    """Validate and persist one idempotent feedback/question record."""

    question_value = question.strip() if isinstance(question, str) else ""
    if len(question_value) < 5:
        return _failure("question must be meaningful and at least 5 characters")

    fingerprint = _fingerprint("feedback", question_value)
    created_at = _utc_now()
    try:
        with _connect() as connection:
            _initialize_schema(connection)
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO feedback
                    (fingerprint, question, created_at)
                VALUES (?, ?, ?)
                """,
                (fingerprint, question_value, created_at),
            )
            row = connection.execute(
                "SELECT id, created_at FROM feedback WHERE fingerprint = ?",
                (fingerprint,),
            ).fetchone()
        if row is None:
            return _failure("feedback could not be persisted")
        duplicate = cursor.rowcount == 0
        logger.info("record_feedback persisted id=%s duplicate=%s", row["id"], duplicate)
        return {
            "success": True,
            "record_type": "feedback",
            "record_id": row["id"],
            "created_at": row["created_at"],
            "duplicate": duplicate,
            "message": "Feedback recorded for follow-up.",
        }
    except sqlite3.Error:
        logger.exception("Failed to persist feedback")
        return _failure("feedback could not be persisted")


def _connect() -> sqlite3.Connection:
    data_dir = load_settings().data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(data_dir / "customer_records.sqlite3")
    connection.row_factory = sqlite3.Row
    return connection


def _initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS customer_interest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT NOT NULL UNIQUE,
            question TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )


def _fingerprint(record_type: str, *values: str) -> str:
    normalized = "\x1f".join(value.casefold() for value in values)
    return hashlib.sha256(f"{record_type}\x1e{normalized}".encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _failure(error: str) -> dict[str, Any]:
    return {"success": False, "error": error}
