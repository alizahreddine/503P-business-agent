import json
import sqlite3

from src.tools import TOOL_SCHEMAS, record_customer_interest, record_feedback


def test_interest_is_persisted_and_duplicate_is_idempotent(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))

    first = record_customer_interest(
        "SAM@example.com", "Sam Student", "Interested in EECE 210 tutoring."
    )
    second = record_customer_interest(
        "sam@example.com", "Sam Student", "Interested in EECE 210 tutoring."
    )

    assert first["success"] is True
    assert first["duplicate"] is False
    assert second["success"] is True
    assert second["duplicate"] is True
    assert second["record_id"] == first["record_id"]

    with sqlite3.connect(tmp_path / "customer_records.sqlite3") as connection:
        rows = connection.execute(
            "SELECT email, name, message, created_at FROM customer_interest"
        ).fetchall()
    assert rows == [
        ("sam@example.com", "Sam Student", "Interested in EECE 210 tutoring.", rows[0][3])
    ]
    assert rows[0][3]


def test_interest_validation_does_not_write(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))

    invalid_email = record_customer_interest("not-an-email", "Sam", "EECE 210")
    missing_name = record_customer_interest("sam@example.com", " ", "EECE 210")
    missing_message = record_customer_interest("sam@example.com", "Sam", " ")

    assert invalid_email["success"] is False
    assert missing_name["success"] is False
    assert missing_message["success"] is False
    assert not (tmp_path / "customer_records.sqlite3").exists()


def test_interest_requires_course_context(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))

    result = record_customer_interest("sam@example.com", "Sam", "Please contact me.")

    assert result["success"] is False
    assert "course interest" in result["error"]
    assert not (tmp_path / "customer_records.sqlite3").exists()


def test_feedback_is_persisted_and_duplicate_is_idempotent(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))

    first = record_feedback("Which tutor supports EECE 230?")
    second = record_feedback(" Which tutor supports EECE 230? ")

    assert first["success"] is True
    assert second["success"] is True
    assert second["duplicate"] is True
    assert first["record_id"] == second["record_id"]
    with sqlite3.connect(tmp_path / "customer_records.sqlite3") as connection:
        row = connection.execute(
            "SELECT question, created_at FROM feedback"
        ).fetchone()
    assert row[0] == "Which tutor supports EECE 230?"
    assert row[1]


def test_feedback_rejects_meaningless_question(monkeypatch, tmp_path):
    monkeypatch.setenv("THE_A_WAY_DATA_DIR", str(tmp_path))

    result = record_feedback("why")

    assert result["success"] is False
    assert "meaningful" in result["error"]
    assert not (tmp_path / "customer_records.sqlite3").exists()


def test_schemas_document_provider_contract():
    functions = {entry["function"]["name"]: entry["function"] for entry in TOOL_SCHEMAS}

    assert set(functions) == {"record_customer_interest", "record_feedback"}
    interest = functions["record_customer_interest"]["parameters"]
    assert interest["required"] == ["email", "name", "message"]
    assert interest["properties"]["email"]["type"] == "string"
    assert interest["properties"]["name"]["type"] == "string"
    assert interest["properties"]["message"]["type"] == "string"
    feedback = functions["record_feedback"]["parameters"]
    assert feedback["required"] == ["question"]
    assert feedback["properties"]["question"]["type"] == "string"
    json.dumps(TOOL_SCHEMAS)
