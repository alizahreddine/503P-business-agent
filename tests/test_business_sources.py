from pathlib import Path

from src.business_sources import EXPECTED_COURSE_CODES, load_business_sources
from src.llm_client import load_business_knowledge


ROOT = Path(__file__).resolve().parents[1]


def test_business_sources_extract_without_conflicts():
    sources = load_business_sources(
        ROOT / "me" / "about_business.pdf",
        ROOT / "me" / "business_summary.txt",
        ROOT / "data" / "course_catalog.json",
    )

    assert sources.conflicts == ()
    assert [course["code"] for course in sources.catalog["catalog_courses"]] == list(
        EXPECTED_COURSE_CODES
    )
    assert sources.catalog["active_offerings"] == []
    assert "mission" in sources.summary_text.lower()
    assert "university tutoring" in sources.pdf_text.lower()


def test_model_knowledge_includes_all_three_required_sources():
    knowledge = load_business_knowledge(ROOT)

    assert "BUSINESS PROFILE PDF (EXTRACTED TEXT):" in knowledge
    assert "BUSINESS SUMMARY:" in knowledge
    assert "COURSE CATALOG JSON:" in knowledge
    assert knowledge.count("The A Way") >= 3
