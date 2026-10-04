"""
Verified admission data for Rahbar AI.
Scope: NUST only, BS Computer Science, 2026 cycle.
Sources: NUST official admissions pages.
Every record carries source_url + verification_state.
"""

# ---------------------------------------------------------------------------
# Universities
# ---------------------------------------------------------------------------
UNIVERSITIES = {
    "NUST": {
        "university_id": "NUST",
        "name": "National University of Sciences and Technology",
        "official_domain": "nust.edu.pk",
        "campuses": ["Islamabad", "SEECS"],
        "programs": ["BS Computer Science"],
        "verification_state": "VERIFIED",
    },
}


# ---------------------------------------------------------------------------
# Formulas — keyed by f"{university}_{program_code}_{cycle}"
# Weights must sum to 1.0
# ---------------------------------------------------------------------------
FORMULAS = {
    "NUST_BSCS_2026": {
        "formula_id": "NUST_BSCS_2026",
        "university": "NUST",
        "program": "BS Computer Science",
        "cycle": "2026",
        "components": {
            "entry_test": 0.75,
            "ssc": 0.10,
            "hssc": 0.15,
        },
        "calculation_method": "weighted_sum",
        "source_id": "NUST_MERIT_CRITERIA",
        "source_url": "https://nust.edu.pk/admissions/undergraduates/merit-criteria-for-admission-on-net-basis/",
        "verification_state": "VERIFIED",
    },
}


# ---------------------------------------------------------------------------
# Eligibility rules — keyed the same way
# ---------------------------------------------------------------------------
ELIGIBILITY_RULES = {
    "NUST_BSCS_2026": {
        "rule_id": "NUST_BSCS_ELIG_2026",
        "university": "NUST",
        "program": "BS Computer Science",
        "cycle": "2026",
        "min_ssc": 60.0,
        "min_hssc": 60.0,
        "eligible_groups": ["Pre-Engineering", "ICS", "Pre-Medical"],
        "min_entry_test": 0.0,
        "source_url": "https://nust.edu.pk/admissions/undergraduates/eligibility-criteria-for-ug-programmes/",
        "verification_state": "VERIFIED",
    },
}


# ---------------------------------------------------------------------------
# Deadlines
# ---------------------------------------------------------------------------
DEADLINES = {
    "NUST_BSCS_2026": {
        "deadline_id": "NUST_BSCS_DEADLINE_2026",
        "university": "NUST",
        "program": "BS Computer Science",
        "cycle": "2026",
        "opening_date": "2026-05-01",
        "closing_date": "2026-06-18",
        "deadline_type": "application",
        "status": "CLOSED",
        "source_url": "https://nust.edu.pk/admissions/undergraduates/dates-to-remember/",
        "verification_state": "VERIFIED",
    },
}


# ---------------------------------------------------------------------------
# Program code mapping + convenience getters
# ---------------------------------------------------------------------------
PROGRAM_CODES = {
    "BS Computer Science": "BSCS",
}


def _make_key(university: str, program: str, cycle: str) -> str:
    code = PROGRAM_CODES.get(program, program.replace(" ", "").upper())
    return f"{university}_{code}_{cycle}"


def get_formula_record(university: str, program: str, cycle: str) -> dict | None:
    return FORMULAS.get(_make_key(university, program, cycle))


def get_eligibility_record(university: str, program: str, cycle: str) -> dict | None:
    return ELIGIBILITY_RULES.get(_make_key(university, program, cycle))


def get_deadline_record(university: str, program: str, cycle: str) -> dict | None:
    return DEADLINES.get(_make_key(university, program, cycle))