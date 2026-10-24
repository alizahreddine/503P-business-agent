from types import SimpleNamespace

import gradio as gr

from src.gradio_app import EXAMPLES, REGISTRATION_NOTICE, WELCOME, create_interface


def test_interface_contains_public_identity_and_notice():
    interface = create_interface()

    assert isinstance(interface, gr.Blocks)
    config = interface.get_config_file()
    serialized = str(config)
    assert "The A Way" in serialized
    assert "Student Concierge" in serialized
    assert REGISTRATION_NOTICE in serialized
    assert WELCOME in serialized
    for example in EXAMPLES:
        assert example in serialized


def test_request_session_hash_is_available_to_gradio_handler():
    request = SimpleNamespace(session_hash="browser-session")

    assert request.session_hash == "browser-session"
