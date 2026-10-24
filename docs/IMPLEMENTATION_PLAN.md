# The A Way Student-Facing AI Tutor — Implementation Plan

## 1. Delivery approach

The assignment is implemented as a self-contained notebook-first prototype. The
notebook uses a deterministic business knowledge bundle and provider adapter so
routing and tools can be tested without a live API call. A live OpenAI path is
included for the final demo, with the key supplied through the environment
rather than committed files. The work packages below record the implementation
sequence and acceptance criteria used for the completed build.

## 2. Repository layout

```text
business_bot/
├── docs/
│   ├── SPEC.md
│   └── IMPLEMENTATION_PLAN.md
├── me/
│   ├── about_business.pdf
│   └── business_summary.txt
├── business_agent.ipynb
├── requirements.txt
└── .env.example
```

The real `.env` remains local and untracked. `app.py` provides the optional
standalone Gradio launch entry point.

## 3. Work packages

### WP1 — Prepare authoritative business content

1. Convert the business identity, mission, services, team framing, value
   proposition, catalog, and limitations into `me/business_summary.txt`.
2. Produce `me/about_business.pdf` with equivalent content and clear headings.
3. Add a knowledge object that labels:
   - catalog courses;
   - verified active offerings (initially empty unless a source explicitly
     supplies records);
   - documented capabilities and limitations;
   - non-facts that must not be inferred.
4. Review both artifacts against the capabilities guide for consistency.

**Exit criteria:** The content is readable, internally consistent, and has no
fabricated price, schedule, tutor, capacity, enrollment, payment, or availability
claim.

### WP2 — Define persona, instructions, and context assembly

1. Add a clearly labeled `PERSONA` block.
2. Add a clearly labeled `INSTRUCTIONS` block containing the guardrails in
   `SPEC.md`.
3. Build `system_prompt` from those blocks plus the business summary and
   catalog/active-offering policy.
4. Add a response policy for unknown facts: qualify the limitation, offer lead
   capture where appropriate, and log an unanswered question through the
   feedback tool.

**Exit criteria:** A notebook reader can distinguish tone/identity from
operational rules, and prompt tests show that the assistant does not turn
catalog membership into active availability.

### WP3 — Build and test the three-way router

1. Implement `route_intent(message)` with the simplest reliable approach:
   deterministic phrase/field checks first, with an optional model fallback only
   if needed.
2. Normalize output to exactly:
   `general_question`, `lead_collection`, or `feedback_unanswered`.
3. Keep the router independent from tool execution so it can be unit tested.
4. Log the selected intent in demonstrations.

**Exit criteria:** General academy questions, expressions of interest, and
feedback/unknown questions take separate paths; ambiguous messages are handled
without inventing a fourth intent.

### WP4 — Implement tool contracts

1. Implement `record_customer_interest(email, name, message)`.
2. Implement `record_feedback(question)`.
3. Validate required strings and reject empty/invalid values explicitly.
4. Log each accepted record with a timestamp and non-sensitive local identifier.
5. Return structured results suitable for a model tool-result message.
6. Define provider-neutral schemas, then translate them to OpenAI or Gemini
   format in one adapter layer.

**Exit criteria:** Direct calls and mocked model tool calls both execute the
correct function, invalid arguments do not produce success-shaped results, and
logs are visible during demos.

### WP5 — Add model adapter and short-term memory

1. Select one provider (OpenAI or Gemini) and pin compatible dependencies.
2. Read the API key from an environment variable or local `.env`.
3. Implement a provider adapter that sends:
   system prompt, recent history, current message, router intent, and tool
   schemas.
4. Handle the complete tool loop: model tool call → local function → tool result
   → final model response.
5. Keep per-session short-term history as role/content messages.
6. Trim history to a documented maximum number of turns and never persist it as
   academy operational data.
7. Surface provider errors and missing configuration clearly.

**Exit criteria:** A mocked provider verifies request shape and tool round trips;
the live path works with a valid local key; history supports a follow-up without
unbounded prompt growth.

### WP6 — Integrate Gradio

1. Wrap the same tested handler in `gr.ChatInterface`.
2. Pass Gradio history into the bounded history adapter.
3. Display only user-safe responses in the chat.
4. Keep tool and router logs available in notebook output or a clearly labeled
   debug component, without exposing keys or raw sensitive data.
5. Add a launch cell that is optional for headless test execution.

**Exit criteria:** The interface starts, accepts a message, preserves a turn, and
uses the same routing and tool behavior as direct notebook calls.

### WP7 — Add demonstrations and verification

Create executable cells for:

| Scenario | Expected route/result |
|---|---|
| “What does The A Way help students with?” | General answer from the business context. |
| “Is EECE 210 offered this semester and at what price?” | Catalog distinction; no availability or price invented. |
| “I’m interested in CMPS 203; I’m Sam, sam@example.com.” | Lead path asks for/records complete name, email, and notes. |
| “Do you have a Saturday tutor for an unlisted course?” | Unknown path calls `record_feedback`. |
| “What did I say I was interested in?” | Short-term history retrieves the prior turn. |
| “Register me and charge my account.” | Out-of-scope redirect; no claim of registration or payment. |

Run notebook cells from a clean kernel, then run focused tests for routing,
schemas, tools, non-fabrication, history limits, provider mocking, and Gradio
handler behavior.

## 4. Test strategy

### Unit tests

- Router labels and ambiguous-input behavior.
- Tool argument validation and structured results.
- Schema required fields, types, and additional-property rejection.
- History append/trim behavior.
- Catalog versus active-offering lookup behavior.
- Out-of-scope response policy.

### Integration tests

- Mocked OpenAI/Gemini request and response shape.
- Tool-call loop with both tools.
- Missing API key and provider error reporting.
- Notebook handler with a representative history.

### Acceptance/demo tests

- Execute the notebook top to bottom in a clean runtime.
- Launch `ChatInterface` and send a sample turn.
- Run every scenario in WP7 and inspect router/tool logs.
- Confirm no output contains secrets or claims unsupported by the source bundle.

## 5. Requirement traceability

| Assignment/spec requirement | Planned work | Verification |
|---|---|---|
| Business PDF and short summary | WP1 | Artifact parity review and file existence check. |
| Separate persona and instructions | WP2 | Notebook inspection plus behavioral prompt tests. |
| Three-way intent router | WP3 | Table-driven route tests and demo logs. |
| `record_customer_interest` | WP4 | Direct and mocked tool-call tests with complete/invalid inputs. |
| `record_feedback` | WP4 | Direct and mocked tool-call tests for unanswered questions and empty input. |
| Tool schemas | WP4 | JSON/schema validation and provider translation test. |
| OpenAI or Gemini integration | WP5 | Mocked round trip, then live smoke test with local key. |
| Short-term conversation history | WP5 | Follow-up scenario and bounded-history assertion. |
| Gradio ChatInterface | WP6 | Handler smoke test and interface launch test. |
| Executable `business_agent.ipynb` | WP5–WP7 | Clean-kernel top-to-bottom execution. |
| Demonstration scenarios | WP7 | Six scenario assertions and visible logs. |
| Catalog/active-offering distinction | WP1, WP2, WP7 | Unverified availability/price test must qualify, not fabricate. |
| No invented facts | WP1, WP2, WP7 | Price, schedule, tutor, capacity, and payment adversarial prompts. |
| Out-of-scope exclusions | WP2, WP7 | Registration, payment, admin, reporting, and portal prompts. |

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| A language model invents live offerings | Keep active offerings separate and empty unless verified; add explicit prompt and adversarial tests. |
| Tool call is skipped for an unknown question | Router marks unknown/feedback intent and tests assert the feedback function was called. |
| Tool call produces false enrollment or payment confirmation | Tool results and instructions explicitly limit confirmation to “interest/feedback recorded.” |
| API provider formats differ | Isolate provider translation behind a small adapter and test the normalized tool contract. |
| Chat history grows without bound | Enforce a fixed turn/message window before every model request. |
| Notebook works only in cell order from a prior session | Execute from a clean kernel and keep setup/import/configuration cells explicit. |
| Secrets leak into the notebook or logs | Use environment variables, `.env.example`, redaction, and a secret-output test. |
| The source guide describes admin features, not student access | Phrase them as documented academy capabilities and redirect admin-only actions. |

## 7. Definition of done

Implementation may begin only after this plan is approved. It is complete when
WP1–WP7 exit criteria pass, the traceability matrix is satisfied, the notebook
executes cleanly, and the demonstration video can show routing, both tools,
history, Gradio, and non-fabrication without relying on invented business data.
