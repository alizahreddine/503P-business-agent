"""Public Gradio interface for The A Way Student Concierge."""

from __future__ import annotations

import logging
import uuid
from typing import Any

import gradio as gr

from src.assistant import StudentConcierge

logger = logging.getLogger(__name__)

WELCOME = (
    "Welcome to The A Way! I’m your Student Concierge. "
    "I can answer questions about our documented tutoring services, record "
    "interest, and capture feedback."
)
REGISTRATION_NOTICE = (
    "Notice: an inquiry or interest submission does not constitute confirmed "
    "course registration or enrollment."
)
EXAMPLES = [
    "What courses do you teach?",
    "I want to join EECE 210.",
    "I have a question about tutoring.",
]


def create_interface(agent: StudentConcierge | None = None) -> gr.Blocks:
    """Create the Gradio Blocks app containing a ChatInterface."""

    concierge = agent or StudentConcierge()

    def chat_handler(
        message: str,
        history: list[Any],
        request: gr.Request | None = None,
    ) -> str:
        session_id = getattr(request, "session_hash", None) or str(uuid.uuid4())
        try:
            return concierge.respond(session_id, message)
        except Exception:
            logger.exception("Unexpected public chat-handler failure")
            return (
                "I’m sorry, something went wrong while handling that message. "
                "Please try again."
            )

    def reset_handler(request: gr.Request | None = None) -> None:
        session_id = getattr(request, "session_hash", None)
        if session_id:
            concierge.reset(session_id)

    with gr.Blocks(
        title="The A Way Student Concierge",
        theme=gr.themes.Soft(),
    ) as interface:
        gr.Markdown(
            "# The A Way\n"
            "### Student Concierge\n\n"
            f"{WELCOME}\n\n"
            f"> {REGISTRATION_NOTICE}"
        )
        chatbot = gr.ChatInterface(
            fn=chat_handler,
            title="Chat with your academic-support assistant",
            description=(
                "Ask about documented academy services and catalog courses. "
                "I will clearly label information that is unavailable or unconfirmed."
            ),
            examples=EXAMPLES,
            cache_examples=False,
            chatbot=gr.Chatbot(
                label="Conversation",
                height=480,
                show_copy_button=True,
            ),
            textbox=gr.Textbox(
                placeholder="Ask a question or share your interest...",
                label="Your message",
            ),
            submit_btn="Send",
            clear_btn="Clear chat",
        )
        reset_button = gr.Button("Reset conversation", variant="secondary")
        reset_button.click(fn=reset_handler, inputs=None, outputs=None)
        gr.Markdown(
            "The A Way provides fictional demo information for this assignment. "
            "Do not enter passwords, payment details, or private student information."
        )
    return interface
