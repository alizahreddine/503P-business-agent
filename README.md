# The A Way Student-Facing AI Agent

This repository is the complete notebook-first submission for the C3 agent
assignment. The assistant represents the fictional The A Way tutoring academy,
answers source-grounded questions, collects prospective-student interest, logs
feedback and unanswered questions, retains bounded session history, and runs in
a Gradio chat interface.

## Current status

Implemented:

- OpenAI Python SDK dependency selection
- Environment-backed runtime configuration
- Import-safe `app.py`
- Executable assignment notebook with six reproducible demonstrations
- Local runtime storage directory
- Fictional business PDF and text summary
- Catalog JSON with no active offerings claimed
- PDF/TXT/JSON loader and source consistency report
- SQLite-backed customer-interest and feedback tools with idempotent writes
- OpenAI client adapter with validated tool-calling loop
- Three-way intent router with explicit model routing instructions
- Session-isolated, bounded short-term conversation memory
- Gradio `ChatInterface` and local launch path
- Unit tests that do not require an API key

## Local setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m pytest
python app.py
```

`OPENAI_API_KEY` may remain empty for imports, deterministic tests, and the
notebook's scripted demonstrations. Set a real key to ask general questions or
exercise model-driven feedback handling in the live Gradio application.

Run `python app.py` from the repository root to launch the local Gradio
interface. Open the local URL printed by Gradio. A configured
`OPENAI_API_KEY` is required for general model answers; lead slot collection
and the public error message remain safe when the key is unavailable.

The OpenAI adapter is implemented in `src/llm_client.py`. It supplies extracted
PDF text, the business summary, catalog JSON, the system prompt, recent history,
and both tool definitions to the model. Normal tests inject a fake provider and
never make network calls. Live checks are separate and skipped by default:

```powershell
$env:RUN_LIVE_LLM_TESTS = "1"
$env:OPENAI_API_KEY = "your-local-key"
python -m pytest tests/test_live_llm.py -q
```

The adapter handles text responses, validated tool calls, timeout/authentication
failures, rate limits, connection/provider errors, malformed tool arguments, and
missing API-key configuration with structured failure results.

Run the complete deterministic requirements audit with:

```powershell
python -m pytest tests/test_requirements_audit.py -q
```

The audit covers known and unsupported questions, course guidance, complete and
multi-turn leads, invalid email, feedback persistence, duplicate prevention,
mixed intents, history and session isolation, failed requests, malformed tool
arguments, prompt injection, and Gradio startup. Live tests are separate and
skipped unless explicitly enabled.

The application writes only local runtime data under `data/`. Generated
customer records and `.env` are ignored by Git.

A ready-to-follow recording walkthrough is available in
`docs/DEMO_SCRIPT.md` for the required submission video.

## Colab setup

1. Clone the repository into the runtime (recommended), or upload
   `business_agent.ipynb`, `requirements.txt`, `src/`, `me/`, and
   `data/course_catalog.json`.
2. Install dependencies in a notebook cell:

   ```python
   %pip install -r requirements.txt
   ```

3. Store the key in Colab Secrets as `OPENAI_API_KEY` for live model calls. Do
   not paste or commit the key in a notebook.
4. Run all notebook cells. The required demonstrations run without a key. To
   launch Gradio, uncomment the final `interface.launch()` line or run:

   ```python
   from src.gradio_app import create_interface
   create_interface().launch()
   ```

   Keep API keys in Colab Secrets or environment variables; never print them.

## Configuration

Configuration is loaded by `src/config.py` using environment variables:

- `OPENAI_API_KEY` — optional for tests/demos, required for live model calls.
- `OPENAI_MODEL` — defaults to `gpt-4o-mini`.
- `THE_A_WAY_DATA_DIR` — defaults to `data`.
- `THE_A_WAY_MAX_HISTORY_MESSAGES` — defaults to `12`.

## Project layout

```text
business_agent.ipynb  # Complete notebook, demos, and Gradio construction
app.py                # Local Gradio application entry point
src/                  # Router, tools, model adapter, memory, and UI
tests/                # Deterministic and opt-in live tests
me/                   # Required business PDF and text summary
data/                 # Catalog plus ignored local runtime records
docs/                 # Detailed specification and implementation plan
```
