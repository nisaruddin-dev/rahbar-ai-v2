"""
Tools for Rahbar AI.
Every tool returns the exact ToolResult envelope from contracts.py.
Every tool catches its own exceptions. Tools never raise.
"""

from datetime import datetime

import rag
import rules_engine
from contracts import ToolResult


# ---------------------------------------------------------------------------
# search_universities
# ---------------------------------------------------------------------------
def search_universities(
    query: str,
    university: str | None = None,
    cycle: str | None = None,
    section: str | None = None,
    program: str | None = None,
) -> ToolResult:
    try:
        results = rag.search(
            query,
            university=university,
            cycle=cycle,
            section=section,
            program=program,
            k=5,
        )

        if not results:
            return {
                "ok": True,
                "error": None,
                "raw": {"chunks": [], "count": 0},
                "summary": "No verified evidence found for this query.",
                "source": None,
            }

        top = results[0]
        meta = top["metadata"]

        return {
            "ok": True,
            "error": None,
            "raw": {"chunks": results, "count": len(results)},
            "summary": f"Found {len(results)} relevant chunks. Top match: {meta.get('section')}.",
            "source": {
                "title": meta.get("section"),
                "url": meta.get("source_url"),
                "university": meta.get("university"),
                "cycle": meta.get("cycle"),
                "verification_state": meta.get("verification_state"),
            },
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"search_failed: {e}",
            "raw": {},
            "summary": "Search failed.",
            "source": None,
        }


# ---------------------------------------------------------------------------
# calculate_aggregate
# ---------------------------------------------------------------------------
def calculate_aggregate(
    university: str,
    program: str,
    cycle: str,
    marks: dict,
) -> ToolResult:
    try:
        result = rules_engine.calculate_aggregate(
            university, program, cycle, marks
        )
        if not result.get("ok"):
            return {
                "ok": False,
                "error": result.get("error"),
                "raw": {},
                "summary": f"Calculation not possible: {result.get('error')}.",
                "source": None,
            }

        return {
            "ok": True,
            "error": None,
            "raw": result,
            "summary": f"Aggregate: {result['aggregate']}%.",
            "source": {
                "title": "Merit formula",
                "url": result.get("source_url"),
                "formula_id": result.get("formula_id"),
            },
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"calculate_failed: {e}",
            "raw": {},
            "summary": "Calculation failed.",
            "source": None,
        }


# ---------------------------------------------------------------------------
# check_deadline
# ---------------------------------------------------------------------------
def check_deadline(
    university: str,
    program: str,
    cycle: str,
    current_datetime: str | None = None,
) -> ToolResult:
    try:
        now = current_datetime or datetime.now().isoformat()
        result = rules_engine.evaluate_deadline(university, program, cycle, now)

        if not result.get("ok"):
            return {
                "ok": False,
                "error": result.get("error"),
                "raw": {},
                "summary": f"Deadline not available: {result.get('error')}.",
                "source": None,
            }

        return {
            "ok": True,
            "error": None,
            "raw": result,
            "summary": (
                f"Deadline status: {result['status']} "
                f"({result['days_remaining']} days remaining)."
            ),
            "source": {
                "title": "Dates to remember",
                "url": result.get("source_url"),
                "closing_date": result.get("closing_date"),
            },
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"deadline_failed: {e}",
            "raw": {},
            "summary": "Deadline check failed.",
            "source": None,
        }