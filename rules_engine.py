"""
Deterministic rules engine for Rahbar AI.
Pure functions. No LLM. No I/O. No side effects.
Every function is unit-testable in isolation.
"""

from datetime import datetime
from data.universities import (
    get_formula_record,
    get_eligibility_record,
    get_deadline_record,
)


# ---------------------------------------------------------------------------
# validate_percentage
# ---------------------------------------------------------------------------
def validate_percentage(value) -> tuple[bool, str | None]:
    """Return (True, None) if value is a valid 0-100 number."""
    if value is None:
        return False, "missing"
    if isinstance(value, bool):
        return False, "boolean is not a percentage"
    if not isinstance(value, (int, float)):
        return False, "not a number"
    if value < 0 or value > 100:
        return False, "must be between 0 and 100"
    return True, None


# ---------------------------------------------------------------------------
# get_formula
# ---------------------------------------------------------------------------
def get_formula(university: str, program: str, cycle: str) -> dict | None:
    """Return the formula record or None."""
    if not university or not program or not cycle:
        return None
    return get_formula_record(university, program, cycle)


# ---------------------------------------------------------------------------
# calculate_aggregate — deterministic, no LLM
# ---------------------------------------------------------------------------
def calculate_aggregate(
    university: str, program: str, cycle: str, marks: dict
) -> dict:
    """
    Compute the aggregate. Returns:
      {"ok": True, "aggregate": float, "breakdown": {...}, "formula_id": str, "source_url": str}
      {"ok": False, "error": str}
    """
    formula = get_formula(university, program, cycle)
    if not formula:
        return {"ok": False, "error": "formula_not_found"}

    if formula.get("verification_state") != "VERIFIED":
        return {"ok": False, "error": "formula_not_verified"}

    components = formula["components"]
    weighted_sum = 0.0
    breakdown = {}

    for field in ("entry_test", "ssc", "hssc"):
        if field not in components:
            continue
        valid, err = validate_percentage(marks.get(field))
        if not valid:
            return {"ok": False, "error": f"{field}: {err}"}
        contribution = round(marks[field] * components[field], 2)
        breakdown[field] = contribution
        weighted_sum += contribution

    return {
        "ok": True,
        "aggregate": round(weighted_sum, 2),
        "breakdown": breakdown,
        "formula_id": formula["formula_id"],
        "source_url": formula.get("source_url"),
    }


# ---------------------------------------------------------------------------
# check_minimum_requirement
# ---------------------------------------------------------------------------
def check_minimum_requirement(
    university: str, program: str, cycle: str, marks: dict
) -> dict:
    """
    Check academic eligibility floors.
    Returns {"ok": True, "passed": bool, "failures": [...]}
    """
    rule = get_eligibility_record(university, program, cycle)
    if not rule:
        return {"ok": False, "error": "eligibility_rule_not_found"}

    failures = []
    if marks.get("ssc", 0) < rule["min_ssc"]:
        failures.append(
            f"SSC below {rule['min_ssc']}% (you have {marks.get('ssc')}%)"
        )
    if marks.get("hssc", 0) < rule["min_hssc"]:
        failures.append(
            f"HSSC below {rule['min_hssc']}% (you have {marks.get('hssc')}%)"
        )

    return {
        "ok": True,
        "passed": len(failures) == 0,
        "failures": failures,
        "rule_id": rule["rule_id"],
        "source_url": rule.get("source_url"),
    }


# ---------------------------------------------------------------------------
# evaluate_deadline
# ---------------------------------------------------------------------------
def evaluate_deadline(
    university: str, program: str, cycle: str, current_datetime: str
) -> dict:
    """
    Returns:
      {"ok": True, "status": "OPEN|CLOSING_SOON|CLOSED", "days_remaining": int,
       "closing_date": str, "source_url": str}
      {"ok": False, "error": str}
    """
    deadline = get_deadline_record(university, program, cycle)
    if not deadline:
        return {"ok": False, "error": "deadline_not_found"}

    try:
        closing = datetime.fromisoformat(deadline["closing_date"]).date()
        now = datetime.fromisoformat(current_datetime).date()
    except Exception as e:
        return {"ok": False, "error": f"date_parse_failed: {e}"}

    days_remaining = (closing - now).days

    if days_remaining < 0:
        status = "CLOSED"
    elif days_remaining <= 7:
        status = "CLOSING_SOON"
    else:
        status = "OPEN"

    return {
        "ok": True,
        "status": status,
        "days_remaining": days_remaining,
        "closing_date": deadline["closing_date"],
        "source_url": deadline.get("source_url"),
    }