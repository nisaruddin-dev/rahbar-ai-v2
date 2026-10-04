# Rahbar AI

Verified admission decision-support for Pakistani FSc students.

## What it does

A student enters their FSc marks, selects a target university and programme,
and asks a natural-language question. Rahbar retrieves verified admission
evidence, calculates the merit aggregate deterministically, checks the
deadline, and returns one of four decisions:

- YES — eligible and actionable now
- NO — fails a verified requirement
- CONDITIONAL — eligible subject to a stated condition
- NOT_YET_VERIFIED — no verified evidence available

Decision support only. Not an admission authority.

## Architecture

- Agent: custom controlled loop, max 4 tool calls, safe-failure gate
- Tools: search_universities, calculate_aggregate, check_deadline
- RAG: Sentence Transformers + FAISS with hard metadata filters
- Rules engine: deterministic math, no LLM in the calculation path
- LLM: used only to explain tool output, never to decide

The agent cannot return YES without a verified source. If evidence is
missing, it returns NOT_YET_VERIFIED rather than guessing.

## Stack

- Python 3.12
- Streamlit
- Sentence Transformers (all-MiniLM-L6-v2)
- FAISS (inner product, L2-normalized)
- Groq (LLM for explanation only)

## Scope

NUST, BS Computer Science, 2026 cycle only. Six verified chunks sourced
from official nust.edu.pk pages.

## Run locally
pip install -r requirements.txt
streamlit run app.py

text

Requires .streamlit/secrets.toml with a GROQ_API_KEY value.

## Design principles

- Rules engine decides. LLM explains.
- RAG retrieves evidence; it does not define truth.
- Every claim is traceable to a nust.edu.pk URL.
- Safe failure over confident fabrication.
- No admission guarantees, ever.