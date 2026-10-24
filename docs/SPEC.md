# The A Way Student-Facing AI Tutor — Specification

## 1. Purpose

The A Way chatbot is a student-facing assistant for a fictional university tutoring
academy. It answers questions about the academy and its tutoring catalog, helps a
prospective student express interest, and records feedback or questions it cannot
answer. It is a conversational front end to curated academy information; it is not
an administrative system and does not replace official enrollment workflows.

This specification adapts the requirements in `C3 - Introduction to Agents.pdf` to
the capabilities and limitations in
`The_A_Way_Academy_Capabilities_Guide.md`.

## 2. Source-of-truth materials and business artifacts

The implementation will create and use these business artifacts:

- `me/about_business.pdf`: the readable business profile required by the
  assignment. It will describe The A Way, its mission, tutoring services, team
  framing, value proposition, catalog, and student-facing boundaries.
- `me/business_summary.txt`: a short, plain-text source used in the system prompt
  and/or retrieval context. It must agree with the PDF.
- `The_A_Way_Academy_Capabilities_Guide.md`: the capabilities reference used to
  derive the business summary and guardrails. It is not a live availability feed.

The chatbot must never treat the capability guide, catalog, or examples as proof
that a particular section, tutor, time, price, or seat is currently available.
Only explicitly supplied active-offering data can support an availability claim.

## 3. Business identity and knowledge boundaries

### 3.1 Identity

The A Way is a fictional university tutoring academy supporting university
students with course-focused tutoring, study planning, exam preparation, and
academic follow-up. Its value proposition is approachable, structured academic
support grounded in a defined course catalog and transparent escalation when
information is missing.

The assistant may explain academy concepts such as courses, semesters, tutors,
sessions, leads, follow-ups, and expected tuition as planning information.

### 3.2 Catalog courses versus active offerings

These are separate concepts and must be represented separately in the knowledge
model and responses:

- **Catalog course:** a reusable course definition such as code, title,
  description, notes, and target majors. The safe initial catalog includes
  `EECE 210`, `EECE 230`, `EECE 231`, `EECE 330`, `EECE 442`, `CMPS 201`,
  `CMPS 203`, and `CMPS 211`.
- **Active offering:** a catalog course instantiated for a particular semester
  with explicitly verified offering facts, such as status, tutor, agreed
  session price, schedule, or capacity. The capabilities guide describes the
  administration system but does not provide a complete live offering roster.

When a student asks “Is EECE 210 available?” the assistant must not infer
availability from catalog membership. It should say that the course is in the
catalog, state that current offering details are not present, and offer to record
interest or feedback. It must not invent prices, schedules, tutors, capacity,
semester dates, or registration status. The same rule applies to any course name
not in an explicitly supplied source.

### 3.3 Known academy facts

The assistant may state, with appropriate qualification:

- the current administration system supports course planning, students, tutors,
  teaching assistants, leads, follow-ups, marketing, tasks, tuition planning,
  and financial records;
- expected tuition is a planning estimate based on session count and active
  students’ agreed per-session prices, not billed or collected revenue;
- the current student entry workflow requires an `@mail.aub.edu` address;
- the current calendar view covers September through November 2026;
- safe lead sources include WhatsApp group, Instagram, friend referral, teaching
  assistant, previous student, classroom announcement, and Other.

The assistant should describe these as documented academy capabilities, not as
actions the chatbot itself can perform.

## 4. User experience and supported intents

The entry point is a Gradio `ChatInterface`. Each user message is routed to
exactly one of these three intents:

1. **General question** — answer from the PDF, summary, and explicitly supplied
   offering data.
2. **Lead collection** — collect a prospective student’s name, email, and
   message/notes, then call `record_customer_interest`.
3. **Feedback or unanswered question** — record feedback or a question the
   assistant cannot answer by calling `record_feedback`.

The router may use lightweight heuristics or a model classification call, but it
must expose the selected intent for demonstration and testing. Ambiguous
messages should receive a safe clarification or be routed to feedback rather
than being treated as a factual answer.

The assistant should be concise, friendly, and student-facing. It should ask for
only the information needed for the current intent and should not imply that a
lead submission completes registration.

## 5. Persona and operational instructions

The notebook must contain two visibly separate, labeled blocks:

### Persona

The assistant is a friendly, clear, honest virtual guide for The A Way. It speaks
to students and prospective students in an encouraging, non-administrative tone.
It explains known information plainly and makes uncertainty visible.

### Instructions

The system prompt instructions must require the assistant to:

- stay in the The A Way persona;
- use the business summary and PDF-derived knowledge;
- distinguish catalog courses from verified active offerings;
- never invent prices, schedules, tutors, capacity, availability, registration
  status, student records, payment status, or financial results;
- avoid presenting expected tuition as billed or collected revenue;
- route each message to one of the three supported intents;
- collect name, email, and message/notes before logging customer interest;
- call the feedback tool when it does not know an answer or receives feedback;
- explain that tool logging is not official registration, payment, or support
  resolution;
- avoid exposing administrator-only records or claiming access to portals;
- keep responses suitable for students and avoid requesting sensitive data.

## 6. Required tool-calling functions

Both tools must be callable by the model, implemented in the notebook, visibly
logged (print or file logging), and returned with a user-safe confirmation.
Tool calls must not claim that a lead was enrolled or that feedback was resolved.

### 6.1 `record_customer_interest`

**Purpose:** Record a prospective student’s interest for follow-up.

**MCP-style schema:**

```json
{
  "name": "record_customer_interest",
  "description": "Record a prospective student's interest for academy follow-up.",
  "parameters": {
    "type": "object",
    "properties": {
      "email": {
        "type": "string",
        "description": "Prospective student's email address."
      },
      "name": {
        "type": "string",
        "description": "Prospective student's name."
      },
      "message": {
        "type": "string",
        "description": "Course interest, question, or follow-up notes."
      }
    },
    "required": ["email", "name", "message"],
    "additionalProperties": false
  }
}
```

**Expected output:** A structured success result containing a local record
identifier or timestamp and a confirmation message. Invalid or incomplete input
must produce an explicit validation error and must not log a success.

### 6.2 `record_feedback`

**Purpose:** Record feedback or an unanswered student question for follow-up.

**MCP-style schema:**

```json
{
  "name": "record_feedback",
  "description": "Log feedback or a question the assistant could not answer.",
  "parameters": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": "The student's feedback or unanswered question."
      }
    },
    "required": ["question"],
    "additionalProperties": false
  }
}
```

**Expected output:** A structured success result containing a local record
identifier or timestamp and a confirmation message. Empty input must produce an
explicit validation error and must not log a success.

## 7. Model integration and conversation state

The implementation may use OpenAI or Gemini, selected before implementation.
The notebook must:

- load the API key from an uncommitted `.env` or environment variable;
- fail clearly when the key is missing rather than silently switching behavior;
- send the persona, instructions, business context, router result, and recent
  chat history to the model;
- expose the two tool schemas in the provider’s function/tool format;
- execute returned tool calls, then provide tool results to the model for the
  final user-facing response;
- preserve short-term conversation history for the active chat session;
- cap or trim history to a documented window so prompts remain bounded;
- avoid persisting student data as an administrative database.

## 8. Gradio interface

`business_agent.ipynb` must include a runnable Gradio `ChatInterface` wired to the
same handler used in demonstrations. The UI should show the assistant response,
retain the active conversation history, and make tool activity observable through
safe notebook logs or a clearly labeled debug display. API keys and raw secrets
must never be displayed.

## 9. Demonstration scenarios

The notebook must demonstrate at least:

1. A general question answered from the business context.
2. A catalog-course question where the assistant explicitly avoids claiming an
   active offering.
3. A lead conversation that collects name, email, and notes and calls
   `record_customer_interest`.
4. A feedback or unknown-offering question that calls `record_feedback`.
5. A follow-up turn proving short-term context is retained.
6. A refusal/qualification for an out-of-scope request such as official
   registration, payment, administrator records, or a student portal.

## 10. Out of scope

The chatbot will not provide:

- official student registration or enrollment;
- real payments, payment processing, balances, or financial reporting;
- administrator database access, protected searches, imports, exports, or
  dashboard operations;
- student or tutor login portals;
- fabricated operational records or live availability;
- authoritative tutor assignment, schedule, capacity, or price data absent from a
  verified active-offering source.

## 11. Requirement-to-implementation-and-test matrix

| Requirement | Implementation | Acceptance test |
|---|---|---|
| Business PDF and summary | Create `me/about_business.pdf` and `me/business_summary.txt` from the academy guide; use both as context sources. | Files exist, describe the same identity, and contain no invented prices, schedules, or availability. |
| Separate persona and instructions | Two labeled notebook variables/sections and a composed `system_prompt`. | Notebook inspection finds distinct Persona and Instructions blocks; a prompt test verifies both affect behavior. |
| Three-way intent router | `route_intent(message)` returns only `general_question`, `lead_collection`, or `feedback_unanswered`. | Table-driven examples cover all three labels, plus ambiguous input; no fourth label is emitted. |
| Two required tools | Implement `record_customer_interest(email, name, message)` and `record_feedback(question)` with visible logging. | Mock model tool calls invoke the correct function and produce structured results; invalid inputs fail explicitly. |
| Tool schemas | Provider-compatible schemas matching the JSON definitions above. | Schema validation confirms required fields, types, and no extra properties. |
| OpenAI or Gemini integration | Provider adapter sends context, history, tools, and handles tool-result turns. | With a mocked client, request shape and tool-call round trip are verified; missing API key fails clearly. |
| Short-term conversation history | Per-session bounded message list, trimmed to a documented limit. | A follow-up references prior context; history length never exceeds the limit. |
| Gradio ChatInterface | UI wraps the tested message handler and carries history. | Interface launches in a notebook and a sample message returns a response without exposing secrets. |
| Executable `business_agent.ipynb` | Notebook contains setup, definitions, handler, demos, and launch cell. | Execute all code cells with a configured test/mock key path; no undefined names or stale-order dependency. |
| Demonstration scenarios | Six scenarios in Section 9 with visible expected tool/log outcomes. | Each scenario runs and matches its expected intent, qualification, or tool call. |
| Catalog/active-offering distinction | Separate data structures and prompt rule; only verified offering records may support availability claims. | Ask about a catalog course and an unverified schedule; response qualifies both and invents nothing. |
| No fabrication | Guardrails and source citation/qualification behavior. | Prompt tests for price, schedule, tutor, capacity, and payment return “not documented” behavior. |
| Out-of-scope boundaries | Refusal/redirect rules for admin, registration, payments, reporting, and portals. | Each out-of-scope scenario is declined or redirected without a tool call that implies completion. |

## 12. Definition of done

The deliverable is complete when the PDF and summary agree, the notebook executes
from a clean kernel with configured dependencies, all required tests in the matrix
pass using live or mocked model calls as appropriate, and the demonstrations show
the required routing, tool calls, non-fabrication, and history behavior.
