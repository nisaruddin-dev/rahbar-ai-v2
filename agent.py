"""
Agent for Rahbar AI.
Controlled custom loop — no CrewAI, no LangChain.
Max 4 tool calls. Duplicate detection. Stop conditions. Anti-hallucination gate.
"""

import json
import time
from datetime import datetime

import streamlit as st
from groq import Groq

from contracts import (
    AgentResponse,
    STATUS_NOT_YET_VERIFIED,
    STATUS_YES,
    CONF_HIGH,
    CONF_NOT_VERIFIED,
)
from prompts import SYSTEM_PROMPT, EXPLANATION_PROMPT_TEMPLATE
from tools import search_universities, calculate_aggregate, check_deadline


MAX_TOOL_CALLS = 4
MAX_SECONDS = 25
LLM_MODEL = "openai/gpt-oss-120b"


# ---------------------------------------------------------------------------
# Trace helpers
# ---------------------------------------------------------------------------
def _trace(event: str, tool: str | None = None, summary: str = "") -> dict:
    return {
        "event": event,
        "tool": tool,
        "summary": summary,
        "ts": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------------------
# Routing — which tool does this query need?
# Deterministic, keyword-based, reliable under demo conditions.
# ---------------------------------------------------------------------------
def _decide_tools(query: str, profile: dict) -> list[str]:
    q = query.lower()
    plan = []

    if any(w in q for w in ("eligib", "require", "can i", "apply", "qualify")):
        plan.append("search_universities")
    if any(w in q for w in ("aggregate", "merit", "calculate", "my %", "my percentage")):
        plan.append("calculate_aggregate")
    if any(w in q for w in ("deadline", "open", "closed", "last date", "due")):
        plan.append("check_deadline")

    if not plan:
        plan.append("search_universities")

    return plan[:MAX_TOOL_CALLS]


# ---------------------------------------------------------------------------
# LLM call — explanation only
# ---------------------------------------------------------------------------
def _call_llm(question: str, profile: dict, tool_results: list[dict]) -> dict:
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        return {
            "status": STATUS_NOT_YET_VERIFIED,
            "decision_reason": f"Agent LLM unavailable: {e}",
            "actions": [],
            "confidence": CONF_NOT_VERIFIED,
            "limitations": ["Language model could not be reached."],
        }

    # Compact the tool results for the prompt.
    #
    # IMPORTANT: we now include the actual chunk TEXTS (top 3, truncated)
    # so the LLM has real evidence to evaluate. Without this, the LLM
    # only sees a summary + a URL and refuses to answer anything.
    compact = []
    for tr in tool_results:
        raw = tr["result"].get("raw", {}) or {}
        chunks = raw.get("chunks", []) or []

        evidence_texts = []
        for c in chunks[:3]:
            if not isinstance(c, dict):
                continue
            meta = c.get("metadata") or {}
            evidence_texts.append({
                "section": meta.get("section", ""),
                "text": str(c.get("text", ""))[:500],
                "url": meta.get("source_url", ""),
            })

        compact.append({
            "tool": tr["tool"],
            "ok": tr["result"].get("ok"),
            "summary": tr["result"].get("summary"),
            "source": tr["result"].get("source"),
            "raw_aggregate": raw.get("aggregate"),
            "raw_status": raw.get("status"),
            "raw_closing_date": raw.get("closing_date"),
            "raw_days_remaining": raw.get("days_remaining"),
            "evidence": evidence_texts,
        })

    prompt = EXPLANATION_PROMPT_TEMPLATE.format(
        profile=json.dumps(profile, indent=2, default=str),
        question=question,
        tool_results=json.dumps(compact, indent=2, default=str),
    )

    try:
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            timeout=20,
        )
        raw_text = completion.choices[0].message.content
        parsed = json.loads(raw_text)
        return {
            "status": parsed.get("status", STATUS_NOT_YET_VERIFIED),
            "decision_reason": parsed.get("decision_reason", ""),
            "actions": parsed.get("actions", []),
            "confidence": parsed.get("confidence", CONF_HIGH),
            "limitations": parsed.get("limitations", []),
        }
    except Exception as e:
        return {
            "status": STATUS_NOT_YET_VERIFIED,
            "decision_reason": f"LLM explanation failed: {e}",
            "actions": [],
            "confidence": CONF_NOT_VERIFIED,
            "limitations": ["Language model output could not be parsed."],
        }


# ---------------------------------------------------------------------------
# Anti-hallucination gate
# ---------------------------------------------------------------------------
def _has_verified_evidence(tool_results: list[dict]) -> bool:
    for tr in tool_results:
        if not tr["result"].get("ok"):
            continue
        src = tr["result"].get("source")
        if src and (src.get("url") or src.get("verification_state") == "VERIFIED"):
            return True
    return False


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def run_agent(user_message: str, profile: dict) -> AgentResponse:
    trace: list[dict] = [_trace("agent_started", None, "Agent started")]

    university = profile.get("target_university") or "NUST"
    program = profile.get("target_program") or "BS Computer Science"
    cycle = profile.get("cycle") or "2026"

    planned = _decide_tools(user_message, profile)
    tool_results: list[dict] = []
    seen: set = set()
    start = time.time()

    for tool_name in planned:
        if len(tool_results) >= MAX_TOOL_CALLS:
            trace.append(_trace("agent_stopped", None, "Max tool calls reached"))
            break
        if (time.time() - start) > MAX_SECONDS:
            trace.append(_trace("agent_stopped", None, "Runtime budget exceeded"))
            break

        call_key = tool_name
        if call_key in seen:
            trace.append(_trace("tool_skipped", tool_name, "Duplicate call suppressed"))
            continue
        seen.add(call_key)

        trace.append(_trace("tool_selected", tool_name, f"Selected {tool_name}"))

        if tool_name == "search_universities":
            result = search_universities(
                user_message, university=university, cycle=cycle, program=program
            )
        elif tool_name == "calculate_aggregate":
            marks = {
                "ssc": profile.get("ssc_marks"),
                "hssc": profile.get("hssc_part_i_marks"),
                "entry_test": profile.get("entry_test_percentage"),
            }
            result = calculate_aggregate(university, program, cycle, marks)
        elif tool_name == "check_deadline":
            result = check_deadline(university, program, cycle)
        else:
            continue

        tool_results.append({"tool": tool_name, "result": result})
        trace.append(_trace("tool_completed", tool_name, result.get("summary", "")))

    usable = [tr for tr in tool_results if tr["result"].get("ok")]
    if not usable:
        trace.append(_trace("decision_generated", None, "NOT_YET_VERIFIED"))
        trace.append(_trace("agent_stopped", None, "Safe failure"))
        return {
            "status": STATUS_NOT_YET_VERIFIED,
            "decision_reason": "Rahbar could not verify this from the available sources.",
            "actions": [],
            "evidence": [],
            "confidence": CONF_NOT_VERIFIED,
            "limitations": ["No verified source matched this query."],
            "agent_trace": trace,
        }

    llm_out = _call_llm(user_message, profile, tool_results)

    evidence = []
    for tr in usable:
        src = tr["result"].get("source") or {}
        evidence.append({
            "claim": tr["result"].get("summary", ""),
            "tool": tr["tool"],
            "source_url": src.get("url"),
            "source_title": src.get("title"),
            "verification_state": src.get("verification_state", "VERIFIED"),
        })

    status = llm_out["status"]
    if status == STATUS_YES and not _has_verified_evidence(tool_results):
        status = STATUS_NOT_YET_VERIFIED
        trace.append(_trace("decision_downgraded", None, "YES downgraded — no verified source"))

    trace.append(_trace("decision_generated", None, f"Status: {status}"))
    trace.append(_trace("agent_stopped", None, "Completed"))

    return {
        "status": status,
        "decision_reason": llm_out["decision_reason"] or "Decision produced from tool evidence.",
        "actions": llm_out["actions"],
        "evidence": evidence,
        "confidence": llm_out["confidence"],
        "limitations": llm_out["limitations"] or ["Historical data does not guarantee future admission."],
        "agent_trace": trace,
    }