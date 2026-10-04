# Rahbar AI

Verified admission decision-support for Pakistani FSc students.

Rahbar AI is a controlled agentic system that helps Pakistani FSc students determine what admission opportunities apply to them, whether they can act now, what is urgent, and what they should do next — using verified admission evidence, deterministic rules, deterministic calculation, and a constrained agentic workflow.

Decision support only. Not an admission authority.

---

## Problem

Pakistani FSc students navigating undergraduate admissions face:

- Fragmented information across university websites, prospectuses, PDFs, and notices.
- Time-sensitive deadlines that change without warning.
- Ambiguous rules about whether Part-I applications are accepted while Part-II results are pending.
- Merit formulas that differ by university, programme, campus, and cycle.
- A choice between acting too early, acting too late, or acting on the wrong assumption.

The result is avoidable confusion, missed opportunities, and wrong decisions.

## Solution

Rahbar AI combines four layers into one student workflow:

1. **Verified evidence** — retrieved from official university pages.
2. **Deterministic rules** — eligibility, deadlines, and merit formulas encoded as code, not as guesses.
3. **A constrained agent** — a single agent that selects tools based on the student's question.
4. **Safe failure** — if evidence is missing, Rahbar returns `NOT_YET_VERIFIED` instead of guessing.

Every decision is traceable to an official source URL. Every number is computed deterministically. Every claim that is not supported by evidence is refused.

---

## Architecture

```text
STUDENT QUERY + PROFILE
        |
        v
+-------------------+
|   AGENT           |  run_agent(query, profile)
|   (custom loop)   |  - Max 4 tool calls
+---------+---------+  - Duplicate detection
          |            - 25 s wall-clock cap
          |
          |  selects tools by keyword intent
          |
          +----------------+----------------+
          |                |                |
          v                v                v
+-----------------+ +-----------------+ +-----------------+
| search_         | | calculate_      | | check_          |
| universities    | | aggregate       | | deadline        |
+--------+--------+ +--------+--------+ +--------+--------+
         |                   |                   |
         v                   v                   v
+-----------------+ +-----------------+ +-----------------+
| RAG retrieval   | | RULES ENGINE    | | RULES ENGINE    |
+--------+--------+ +--------+--------+ +--------+--------+
         |                   |                   |
         +-------------------+-------------------+
                             |
                             v
                +-----------------------------+
                | DATA (data/universities.py) |
                | FORMULAS                    |
                | ELIGIBILITY_RULES           |
                | DEADLINES                   |
                +--------------+--------------+
                               |
                               v
                +-----------------------------+
                | LLM (explanation only;      |
                |      does NOT decide)       |
                +--------------+--------------+
                               |
                               v
                +-----------------------------+
                | ANTI-HALLUCINATION GATE     |
                | YES + no verified source    |
                |      -> NOT_YET_VERIFIED    |
                +--------------+--------------+
                               |
                               v
                +-----------------------------+
                | AgentResponse               |
                | status - reason - evidence  |
                | actions - confidence - trace|
                +-----------------------------+
```

**Design principle:** the agent reasons about *what to do*; it cannot manufacture what the university has not verified.

---

## Decision States

Rahbar AI returns exactly one of four decision states:

| State | Meaning |
|---|---|
| `YES` | The student can act under verified conditions. |
| `NO` | The student cannot proceed under verified conditions. |
| `CONDITIONAL` | The student can proceed if a stated condition is satisfied. |
| `NOT_YET_VERIFIED` | Evidence is insufficient to safely determine the answer. |

**Critical rule:** `NOT_YET_VERIFIED` is not `NO`. Safe uncertainty is preferred over forced certainty.

---

## Components

| File | Purpose |
|---|---|
| `contracts.py` | Frozen interfaces: `ToolResult`, `AgentResponse`, `StudentProfile`. |
| `data/universities.py` | Structured admission data: `UNIVERSITIES`, `FORMULAS`, `ELIGIBILITY_RULES`, `DEADLINES`. |
| `rules_engine.py` | Deterministic math. No LLM. `validate_percentage`, `get_formula`, `calculate_aggregate`, `check_minimum_requirement`, `evaluate_deadline`. |
| `rag.py` | Retrieval module. Sentence Transformers + FAISS + hard metadata filters. Returns evidence only. No decisions. |
| `tools.py` | Three tools: `search_universities`, `calculate_aggregate`, `check_deadline`. Every tool returns the exact `ToolResult` envelope. Every tool catches its own exceptions. |
| `memory.py` | Short-term session memory using Streamlit `session_state`. No disk. No cross-session persistence. |
| `prompts.py` | System prompt + explanation template. Enforces grounding, forbids invention, defines query-type rules. |
| `agent.py` | Custom controlled loop. Max 4 tool calls. Duplicate detection. Stop conditions. Anti-hallucination gate. |
| `app.py` | Streamlit UI. Ten sections, decision card, aggregate, evidence grid, actions, limitations, agent trace. |
| `chunks.json` + `metadata.json` + `faiss.index` | Verified evidence retrieved from official university pages. |
| `build_index.py` | One-time ingestion script that rebuilds `faiss.index` from `chunks.json`. |
| `test_golden.py` | Deterministic tests covering aggregate, eligibility, deadline, and RAG behavior. |

---

## Scope

**In scope for this hackathon build:**

- One university, one programme, one admission cycle.
- A small, curated set of verified evidence chunks sourced from official university pages.
- Three tools: `search_universities`, `calculate_aggregate`, `check_deadline`.
- One agent. One decision contract. One trace format.

**Out of scope:**

- Broad multi-university coverage.
- Application submission.
- Long-term memory.
- Voice or mobile interfaces.
- Model fine-tuning.
- Autonomous web browsing.

Scope was deliberately narrowed so that the one path that ships is demonstrably correct rather than broadly claimed.

---

## Agent Rules

The agent enforces six rules at the code level — not the prompt level:

1. **Max 4 tool calls.** If the loop reaches the cap, it stops.
2. **Duplicate call detection.** A `(tool, args)` pair is only executed once.
3. **Runtime cap.** 25 seconds wall-clock maximum.
4. **Anti-hallucination gate.** If the LLM returns `YES` but no tool produced a verified source, the status is downgraded to `NOT_YET_VERIFIED`.
5. **No chain-of-thought exposure.** The trace shows events, tools, and result summaries — never internal reasoning.
6. **Safe failure on missing evidence.** If no tool produced usable data, the agent returns `NOT_YET_VERIFIED` with a limitations list.

---

## Anti-Hallucination Design

Rahbar AI separates four concerns that are often collapsed into one:

| Concern | Owner |
|---|---|
| Retrieval | `rag.py` — returns evidence only. Never decides. |
| Rules | `rules_engine.py` — deterministic math. Never calls an LLM. |
| Decision | The agent loop — applies the four-state model. |
| Explanation | The LLM — describes what the tools already determined. |

The LLM **cannot**:

- Set a status without a verified source.
- Compute an aggregate.
- Override a deterministic rule.
- Invent a deadline, formula, or eligibility threshold.

The LLM **can**:

- Explain the tool output in plain English.
- Produce a personalized action list.
- Surface limitations and confidence.

Two independent layers enforce this: the system prompt and a code-level gate in `agent.py`. Either one alone could be defeated. Together they hold.

---

## Example Queries

**Query 1 — Eligibility**
Am I eligible for the target programme in the current cycle?

text
Response: `YES` — cites the verified minimum threshold and the eligible-groups rule. Part-I evaluation is explicit.

**Query 2 — Aggregate**
What is my aggregate for the target programme?

text
Response: `YES` — shows the deterministic aggregate with breakdown and the formula source URL.

**Query 3 — Combined**
Can I apply? Am I eligible and is the deadline open?

text
Response: `CONDITIONAL` — eligible on Part-I, but the current deadline has closed. Two tools called: `search_universities` + `check_deadline`.

**Query 4 — Failure demonstration**
What is the closing merit for a future cycle?

text
Response: `NOT_YET_VERIFIED` — no verified evidence for that cycle. The agent refuses to guess.

---

## Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Language | Python 3.12 |
| Retrieval | Sentence Transformers (`all-MiniLM-L6-v2`) + FAISS (inner product, L2-normalized) |
| LLM | Groq — `openai/gpt-oss-120b` |
| Rules | Pure Python (no external dependencies) |
| Memory | Streamlit `session_state` |
| Deployment | Streamlit Community Cloud |

No CrewAI. No LangChain. No unnecessary frameworks. The agent is a custom `while` loop — auditable, deterministic, and small enough to read in five minutes.

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/nisaruddin-dev/rahbar-ai-v2.git
cd rahbar-ai-v2

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate      # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key
#    Create .streamlit/secrets.toml with:
#    GROQ_API_KEY = "gsk_your_key_here"

# 5. Run the app
streamlit run app.py
The app opens at http://localhost:8501.

Tests
Deterministic tests run without any LLM:

bash
python test_golden.py
Expected output:

text
[PASS] aggregate.ok: got=True want=True
[PASS] aggregate.value: got=74.25 want=74.25
[PASS] missing_formula.ok: got=False want=False
[PASS] elig_pass: got=True want=True
[PASS] elig_fail: got=False want=False
[PASS] deadline.closed: got=CLOSED want=CLOSED
[PASS] deadline.open: got=OPEN want=OPEN
[PASS] rag.FAST_zero: got=0 want=0
[PASS] rag.NUST_nonzero
[PASS] rag.empty_query: got=0 want=0

All golden tests passed.
Eleven assertions. Zero LLM calls. If these pass, the deterministic core is intact.

Data Provenance
Every record in data/universities.py carries a source_url and a verification_state. Every chunk in chunks.json carries a source_url, a section label, a cycle label, and a verification_state.

All evidence was retrieved from official university pages and verified on 2026-10-04. A second-reviewer sign-off is tracked separately in docs/.

Design Principles
Rules engine decides. LLM explains. Never the reverse.

RAG retrieves evidence; it does not define truth. The agent decides what the evidence means.

Every claim is traceable to an official URL. If it cannot be traced, it is not published.

Safe failure over confident fabrication. NOT_YET_VERIFIED is a legitimate answer.

No admission guarantees, ever. Rahbar advises. The student decides. The university admits.

Roadmap (Post-Hackathon)
Broader university and campus coverage with cycle-scoped records.

Multi-cycle and multi-campus RAG metadata.

Historical competitiveness context with explicit metric-type labels.

A document checklist tool with REQUIRED_NOW / REQUIRED_LATER / CONDITIONAL / NOT_YET_VERIFIED states.

Urdu and Roman Urdu interface options that preserve the underlying decisions.

Long-term memory with explicit privacy controls.

License
Hackathon submission — internal use for judging. Contact the author for other uses.