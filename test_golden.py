"""
Golden tests for Rahbar AI.
Runs deterministic layers only. No LLM required.

    python test_golden.py
"""

from rules_engine import (
    calculate_aggregate,
    check_minimum_requirement,
    evaluate_deadline,
)
import rag


def assert_eq(name, got, want):
    status = "PASS" if got == want else "FAIL"
    print(f"[{status}] {name}: got={got} want={want}")
    if got != want:
        raise SystemExit(1)


def assert_true(name, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}")
    if not condition:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Deterministic math
# ---------------------------------------------------------------------------
def test_calculate_aggregate_nust():
    result = calculate_aggregate(
        "NUST",
        "BS Computer Science",
        "2026",
        {"entry_test": 70, "ssc": 90, "hssc": 85},
    )
    assert_eq("aggregate.ok", result["ok"], True)
    assert_eq("aggregate.value", result["aggregate"], 74.25)


def test_calculate_aggregate_missing_formula():
    result = calculate_aggregate(
        "FAST",
        "BS Computer Science",
        "2026",
        {"entry_test": 70, "ssc": 90, "hssc": 85},
    )
    assert_eq("missing_formula.ok", result["ok"], False)
    assert_eq("missing_formula.error", result["error"], "formula_not_found")


def test_eligibility_pass():
    result = check_minimum_requirement(
        "NUST",
        "BS Computer Science",
        "2026",
        {"ssc": 90, "hssc": 85},
    )
    assert_eq("elig_pass", result["passed"], True)


def test_eligibility_fail():
    result = check_minimum_requirement(
        "NUST",
        "BS Computer Science",
        "2026",
        {"ssc": 50, "hssc": 85},
    )
    assert_eq("elig_fail", result["passed"], False)


def test_deadline_closed():
    result = evaluate_deadline(
        "NUST",
        "BS Computer Science",
        "2026",
        "2026-10-04T00:00:00",
    )
    assert_eq("deadline.closed", result["status"], "CLOSED")


def test_deadline_open():
    result = evaluate_deadline(
        "NUST",
        "BS Computer Science",
        "2026",
        "2026-05-15T00:00:00",
    )
    assert_eq("deadline.open", result["status"], "OPEN")


# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------
def test_rag_isolates_university():
    hits = rag.search("eligibility", university="FAST", cycle="2026")
    assert_eq("rag.FAST_zero", len(hits), 0)


def test_rag_returns_nust():
    hits = rag.search("NUST eligibility", university="NUST", cycle="2026")
    assert_true("rag.NUST_nonzero", len(hits) >= 1)


def test_rag_empty_query():
    hits = rag.search("", university="NUST", cycle="2026")
    assert_eq("rag.empty_query", len(hits), 0)


if __name__ == "__main__":
    test_calculate_aggregate_nust()
    test_calculate_aggregate_missing_formula()
    test_eligibility_pass()
    test_eligibility_fail()
    test_deadline_closed()
    test_deadline_open()
    test_rag_isolates_university()
    test_rag_returns_nust()
    test_rag_empty_query()
    print("\nAll golden tests passed.")