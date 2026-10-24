"""Application entry point for The A Way Student Concierge."""

from __future__ import annotations

from src.config import Settings, load_settings
from src.assistant import StudentConcierge
from src.gradio_app import create_interface
from src.llm_client import OpenAIStudentConcierge, load_business_knowledge


def create_app(settings: Settings | None = None) -> StudentConcierge:
    """Create a session-aware assistant without making an API call."""

    runtime_settings = settings or load_settings()
    runtime_settings.data_dir.mkdir(parents=True, exist_ok=True)
    return StudentConcierge(
        client=OpenAIStudentConcierge(settings=runtime_settings),
        business_knowledge=load_business_knowledge(),
        max_history_messages=runtime_settings.max_history_messages,
    )


def launch(settings: Settings | None = None) -> None:
    """Launch the local Gradio interface."""

    interface = create_interface(create_app(settings))
    interface.launch()


if __name__ == "__main__":
    launch()
