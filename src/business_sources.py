"""Load and cross-check The A Way business source artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader


EXPECTED_COURSE_CODES = (
    "EECE 210",
    "EECE 230",
    "EECE 231",
    "EECE 330",
    "EECE 442",
    "CMPS 201",
    "CMPS 203",
    "CMPS 211",
)


@dataclass(frozen=True)
class BusinessSources:
    """Extracted source content and consistency findings."""

    pdf_text: str
    summary_text: str
    catalog: dict[str, Any]
    conflicts: tuple[str, ...]


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Extract text from every page of the business PDF."""

    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def load_business_sources(
    pdf_path: str | Path,
    summary_path: str | Path,
    catalog_path: str | Path,
) -> BusinessSources:
    """Load PDF, summary, and catalog JSON and report source conflicts."""

    pdf_text = extract_pdf_text(pdf_path)
    summary_text = Path(summary_path).read_text(encoding="utf-8")
    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    conflicts = tuple(_find_conflicts(pdf_text, summary_text, catalog))
    return BusinessSources(pdf_text, summary_text, catalog, conflicts)


def _find_conflicts(
    pdf_text: str,
    summary_text: str,
    catalog: dict[str, Any],
) -> list[str]:
    conflicts: list[str] = []
    if "The A Way" not in pdf_text or "The A Way" not in summary_text:
        conflicts.append("Business name is missing from PDF or summary.")

    json_codes = [
        str(course.get("code", ""))
        for course in catalog.get("catalog_courses", [])
        if isinstance(course, dict)
    ]
    normalized_pdf = re.sub(r"\s+", " ", pdf_text)
    normalized_summary = re.sub(r"\s+", " ", summary_text)
    for code in EXPECTED_COURSE_CODES:
        if code not in normalized_pdf:
            conflicts.append(f"{code} is missing from the PDF.")
        if code not in normalized_summary:
            conflicts.append(f"{code} is missing from the summary.")
        if code not in json_codes:
            conflicts.append(f"{code} is missing from the JSON catalog.")

    if catalog.get("active_offerings") != []:
        conflicts.append("Demo catalog must not claim unverified active offerings.")
    required_unconfirmed = {
        "price",
        "schedule",
        "tutor",
        "capacity",
        "registration_status",
    }
    actual_unconfirmed = set(catalog.get("unconfirmed_fields", []))
    missing_fields = required_unconfirmed - actual_unconfirmed
    if missing_fields:
        conflicts.append(
            "JSON does not mark fields as unconfirmed: "
            + ", ".join(sorted(missing_fields))
        )
    safeguard_phrases = (
        "does not imply an active offering",
        "not proof that a course is currently open",
    )
    if not any(phrase in normalized_summary.lower() for phrase in safeguard_phrases):
        conflicts.append("Summary lacks the catalog/active-offering safeguard.")
    return conflicts


def format_source_report(sources: BusinessSources) -> str:
    """Return a human-readable extraction and conflict report."""

    codes = [
        course["code"]
        for course in sources.catalog.get("catalog_courses", [])
        if isinstance(course, dict) and "code" in course
    ]
    lines = [
        "=== Extracted The A Way business information ===",
        f"Business: {sources.catalog.get('business_name', 'UNKNOWN')}",
        f"Catalog courses ({len(codes)}): {', '.join(codes)}",
        f"Active offerings confirmed: {len(sources.catalog.get('active_offerings', []))}",
        "Unconfirmed fields: "
        + ", ".join(sources.catalog.get("unconfirmed_fields", [])),
        "",
        "=== Source consistency ===",
        "No conflicts found." if not sources.conflicts else "\n".join(
            f"- {conflict}" for conflict in sources.conflicts
        ),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    loaded = load_business_sources(
        root / "me" / "about_business.pdf",
        root / "me" / "business_summary.txt",
        root / "data" / "course_catalog.json",
    )
    print(format_source_report(loaded))
