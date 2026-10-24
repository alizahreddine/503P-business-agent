# C3 Assignment Video Demo Script

Use this sequence for a concise 3–5 minute submission video.

## 1. Show the deliverables

- Open `me/about_business.pdf` and `me/business_summary.txt`.
- Point out the fictional business name, mission, services, team, and value proposition.
- Open `business_agent.ipynb` and show the separately labeled **Persona** and
  **Instructions** cells.

## 2. Run the notebook

Run all cells from a clean kernel. Highlight:

- the conflict-free PDF/TXT/catalog source report;
- the three router labels;
- both printed MCP-style tool schemas;
- all six scenario outputs;
- the logged `record_customer_interest` and `record_feedback` activity;
- the explicit qualification that a catalog course is not a confirmed active offering;
- the refusal to process payment or perform official registration.

The notebook's demonstrations are deterministic and do not require an API key.

## 3. Show the live Gradio app

Create an untracked `.env` from `.env.example`, add a valid `OPENAI_API_KEY`, and run:

```powershell
python app.py
```

In the UI, demonstrate these messages:

1. `What is The A Way?`
2. `Is EECE 210 open, and who teaches it?`
3. `I want to join CMPS 203.` followed by a name and email.
4. `I have a complaint about tutoring.`
5. `Register me now and take my payment.`

Explain that interest and feedback are local follow-up records—not enrollment,
payment, or issue resolution.

## 4. Show verification

Run:

```powershell
python -m pytest -q
```

Show the passing test count. Live OpenAI tests are intentionally opt-in and run
only when `RUN_LIVE_LLM_TESTS=1` and a real key are configured.

## 5. Before publishing

- Confirm `.env`, `data/customer_records.sqlite3`, and notebook checkpoints are absent from the commit.
- Do not expose the API key or real student contact details in the recording.
- Upload the repository and attach or link the recorded video as required by the course submission process.
