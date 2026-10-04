"""
Frozen contracts for Rahbar AI.
DO NOT EDIT after this file is created.
Every module imports its types from here.
"""

from typing import TypedDict, Literal, Any


# ---------------------------------------------------------------------------
# Tool return contract — every tool returns this exact shape
# ---------------------------------------------------------------------------
class ToolResult(TypedDict):
    ok: bool
    error: str | None
    raw: dict[str, Any]
    summary: str
    source: dict[str, Any] | None


# ---------------------------------------------------------------------------
# Student profile — the only shape memory.py stores
# ---------------------------------------------------------------------------
class StudentProfile(TypedDict, total=False):
    academic_level: str
    fsc_stream: str
    ssc_marks: float
    hssc_part_i_marks: float
    hssc_part_ii_status: str
    hssc_part_ii_marks: float
    entry_test_percentage: float
    target_university: str
    target_program: str
    cycle: str


# ---------------------------------------------------------------------------
# Agent response contract — run_agent() returns exactly this shape
# ---------------------------------------------------------------------------
class AgentResponse(TypedDict):
    status: Literal["YES", "NO", "CONDITIONAL", "NOT_YET_VERIFIED"]
    decision_reason: str
    actions: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    confidence: Literal["HIGH", "MEDIUM", "LOW", "NOT_VERIFIED"]
    limitations: list[str]
    agent_trace: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Enums (importable constants so nothing drifts)
# ---------------------------------------------------------------------------
STATUS_YES = "YES"
STATUS_NO = "NO"
STATUS_CONDITIONAL = "CONDITIONAL"
STATUS_NOT_YET_VERIFIED = "NOT_YET_VERIFIED"
STATUS_VALUES = (STATUS_YES, STATUS_NO, STATUS_CONDITIONAL, STATUS_NOT_YET_VERIFIED)

CONF_HIGH = "HIGH"
CONF_MEDIUM = "MEDIUM"
CONF_LOW = "LOW"
CONF_NOT_VERIFIED = "NOT_VERIFIED"
CONFIDENCE_VALUES = (CONF_HIGH, CONF_MEDIUM, CONF_LOW, CONF_NOT_VERIFIED)