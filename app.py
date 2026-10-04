import streamlit as st
from datetime import date
import re
import html

# =========================================================
# AGENT IMPORTS (SAFE)
# =========================================================

try:
    from agent import run_agent
    AGENT_AVAILABLE = True
    AGENT_IMPORT_ERROR = ""
except Exception as e:
    AGENT_AVAILABLE = False
    AGENT_IMPORT_ERROR = str(e)

try:
    from rules_engine import calculate_aggregate
    RULES_AVAILABLE = True
except Exception:
    RULES_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Rahbar AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(59,130,246,0.10), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(99,102,241,0.10), transparent 30%),
        #f8fafc;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 2.5rem 2.8rem;
    border-radius: 28px;
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #172554 50%,
        #1e40af 100%
    );
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 20px 50px rgba(15,23,42,0.20);
    animation: fadeUp 0.7s ease;
}

.hero h1 {
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
}

.hero p {
    font-size: 1.05rem;
    color: #dbeafe;
    margin-top: 0.7rem;
    max-width: 750px;
}

.section-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0f172a;
    margin-top: 1.8rem;
    margin-bottom: 0.8rem;
}

.section-subtitle {
    color: #64748b;
    margin-bottom: 1rem;
}

.card {
    background: rgba(255,255,255,0.90);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 1.35rem;
    box-shadow: 0 8px 30px rgba(15,23,42,0.06);
    transition: all 0.25s ease;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 35px rgba(15,23,42,0.10);
}

.stButton > button {
    border: none;
    border-radius: 14px;
    padding: 0.75rem 1rem;
    font-weight: 700;
    font-size: 1rem;
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: white;
    box-shadow: 0 8px 20px rgba(37,99,235,0.25);
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(37,99,235,0.35);
}

.decision {
    padding: 1.6rem;
    border-radius: 22px;
    margin-bottom: 1rem;
    animation: popIn 0.55s ease;
}

.decision h2 {
    margin-top: 0;
    font-size: 1.7rem;
}

.decision p {
    margin-bottom: 0;
    line-height: 1.65;
}

.yes {
    background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
    border: 1px solid #34d399;
}

.no {
    background: linear-gradient(135deg, #fef2f2, #fff1f2);
    border: 1px solid #fb7185;
}

.conditional {
    background: linear-gradient(135deg, #fffbeb, #fefce8);
    border: 1px solid #fbbf24;
}

.pending {
    background: linear-gradient(135deg, #eff6ff, #eef2ff);
    border: 1px solid #60a5fa;
    color: #0f172a;
}

.pending h2 {
    color: #0f172a;
}

.pending p {
    color: #1e293b;
}

.metric-card {
    text-align: center;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 1.3rem;
    box-shadow: 0 8px 25px rgba(15,23,42,0.06);
}

.metric-number {
    font-size: 2rem;
    font-weight: 800;
    color: #2563eb;
}

.metric-label {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 0.2rem;
}

.evidence-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

.evidence-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #2563eb;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 7px 24px rgba(15,23,42,0.06);
    transition: all 0.2s ease;
}

.evidence-card:hover {
    transform: translateY(-2px);
}

.evidence-title {
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 5px;
}

.evidence-value {
    color: #475569;
}
.action {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    transition: all 0.2s ease;
    color: #0f172a;
}

.action:hover {
    border-color: #93c5fd;
    transform: translateX(4px);
}

.action-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #2563eb;
    color: white;
    font-weight: 800;
    margin-right: 10px;
}

.trace {
    background: #0b1120;
    color: #cbd5e1;
    border-radius: 18px;
    padding: 1.4rem;
    font-family: monospace;
    line-height: 1.9;
    box-shadow: 0 10px 30px rgba(15,23,42,0.15);
}

.trace-step {
    color: #4ade80;
}

.trace-muted {
    color: #94a3b8;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes popIn {
    from {
        opacity: 0;
        transform: scale(0.96);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@media (max-width: 800px) {
    .evidence-grid {
        grid-template-columns: 1fr;
    }

    .hero h1 {
        font-size: 2.2rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "asked" not in st.session_state:
    st.session_state.asked = False

if "decision" not in st.session_state:
    st.session_state.decision = "NOT_YET_VERIFIED"

if "reason" not in st.session_state:
    st.session_state.reason = ""

if "trace_steps" not in st.session_state:
    st.session_state.trace_steps = []

if "show_calculation" not in st.session_state:
    st.session_state.show_calculation = False

if "evidence" not in st.session_state:
    st.session_state.evidence = []

if "actions" not in st.session_state:
    st.session_state.actions = []

if "aggregate_data" not in st.session_state:
    st.session_state.aggregate_data = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def esc(value):
    """Escape any dynamic value before interpolating into HTML.
    Kept even though we now use st.html() — st.html() does NOT
    auto-escape, so escaping dynamic content is still required."""
    return html.escape(str(value if value is not None else ""))


def contains_year(text):
    return [int(x) for x in re.findall(r"\b(20\d{2})\b", text)]


def is_future_or_unavailable_question(text):
    q = text.lower()

    current_year = date.today().year
    years = contains_year(q)

    future_year = any(year > current_year for year in years)

    future_words = [
        "future",
        "next year",
        "upcoming",
        "prediction",
        "predict",
        "expected merit",
        "expected closing merit",
        "closing merit prediction"
    ]

    unavailable_words = [
        "latest",
        "current closing merit",
        "closing merit",
        "cutoff",
        "deadline",
        "merit",
        "eligibility"
    ]

    if future_year:
        return True

    if any(word in q for word in future_words):
        return True

    if any(word in q for word in unavailable_words):
        return True

    return False


def is_calculation_question(text):
    q = text.lower()

    calculation_words = [
        "aggregate",
        "calculate aggregate",
        "calculate my aggregate",
        "calculate my merit",
        "merit calculation",
        "marks",
        "percentage",
        "calculate",
        "how much aggregate",
        "what is my aggregate",
        "what will be my aggregate",
        "aggregate score",
        "merit score"
    ]

    return any(word in q for word in calculation_words)


def is_deadline_question(text):
    q = text.lower()

    deadline_words = [
        "deadline",
        "last date",
        "last date to apply",
        "application date",
        "closing date",
        "when should i apply",
        "when is the deadline"
    ]

    return any(word in q for word in deadline_words)


def normalize_part2_status(value):
    """Convert Minaam's radio values to contract enum values."""
    if value is None:
        return "PENDING"
    v = str(value).strip().upper().replace(" ", "_")
    if v == "NOT_APPLICABLE":
        return "NOT_APPLICABLE"
    if v == "DECLARED":
        return "DECLARED"
    return "PENDING"


def build_student_profile(
    university,
    program,
    campus,
    cycle,
    part2_status,
    ssc_marks,
    hssc_marks,
    hssc_group,
    entry_test
):
    """
    Map Minaam's form fields to the StudentProfile contract shape.

    Minaam field          -> contract key
    -----------------------------------------
    university            -> target_university
    program               -> target_program
    cycle                 -> cycle
    part2_status          -> hssc_part_ii_status  (uppercased)
    ssc_marks             -> ssc_marks
    hssc_marks            -> hssc_part_i_marks
    hssc_group            -> fsc_stream
    entry_test            -> entry_test_percentage
    campus                -> campus (extra, ignored by agent if unknown)
    """
    profile = {
        "target_university": university,
        "target_program": program,
        "cycle": cycle,
        "hssc_part_ii_status": normalize_part2_status(part2_status),
        "ssc_marks": float(ssc_marks),
        "hssc_part_i_marks": float(hssc_marks),
        "fsc_stream": hssc_group,
        "entry_test_percentage": float(entry_test),
        "campus": campus.strip() if campus else "",
        "academic_level": "FSc Part-II",
    }
    return profile


def _get(obj, key, default=None):
    """Read a key from either a dict or an object attribute."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def compute_local_aggregate(entry_test, ssc_marks, hssc_marks):
    """Fallback local aggregate computation (NUST formula)."""
    aggregate = (
        (entry_test * 0.75)
        + (ssc_marks * 0.10)
        + (hssc_marks * 0.15)
    )
    entry_test_contribution = entry_test * 0.75
    academic_contribution = (
        (ssc_marks * 0.10) + (hssc_marks * 0.15)
    )
    return {
        "aggregate": aggregate,
        "entry_test_contribution": entry_test_contribution,
        "academic_contribution": academic_contribution,
        "source": None,
    }


def compute_aggregate(profile, entry_test, ssc_marks, hssc_marks):
    """
    Single source of truth: rules_engine.calculate_aggregate.
    Fallback to local NUST formula only if rules_engine is
    unavailable or returns an unusable result.

    rules_engine.calculate_aggregate signature:
        calculate_aggregate(university, program, cycle, marks_dict)
    """
    if RULES_AVAILABLE:
        result = None
        try:
            result = calculate_aggregate(
                profile["target_university"],
                profile["target_program"],
                profile["cycle"],
                {
                    "entry_test": profile["entry_test_percentage"],
                    "ssc": profile["ssc_marks"],
                    "hssc": profile["hssc_part_i_marks"],
                },
            )
        except Exception:
            result = None

        if result is not None:
            aggregate = _get(result, "aggregate")
            if aggregate is None:
                aggregate = _get(result, "total")
            if aggregate is None:
                aggregate = _get(result, "overall")

            if aggregate is not None:
                try:
                    aggregate = float(aggregate)
                except Exception:
                    aggregate = None

            if aggregate is not None:
                entry_contribution = _get(
                    result, "entry_test_contribution"
                )
                if entry_contribution is None:
                    entry_contribution = entry_test * 0.75

                academic_contribution = _get(
                    result, "academic_contribution"
                )
                if academic_contribution is None:
                    academic_contribution = (
                        (ssc_marks * 0.10) + (hssc_marks * 0.15)
                    )

                return {
                    "aggregate": aggregate,
                    "entry_test_contribution": float(entry_contribution),
                    "academic_contribution": float(academic_contribution),
                    "source": _get(result, "source"),
                }

    # Local fallback (only used when rules_engine is missing or failed)
    return compute_local_aggregate(entry_test, ssc_marks, hssc_marks)


def render_decision(decision, reason):

    safe_reason = esc(reason)

    if decision == "YES":
        st.markdown(
            f"""
            <div class="decision yes">
                <h2>✅ YES</h2>
                <p>{safe_reason}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif decision == "NO":
        st.markdown(
            f"""
            <div class="decision no">
                <h2>❌ NO</h2>
                <p>{safe_reason}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif decision == "CONDITIONAL":
        st.markdown(
            f"""
            <div class="decision conditional">
                <h2>⚠️ CONDITIONAL</h2>
                <p>{safe_reason}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f"""
            <div class="decision pending">
                <h2>🔎 NOT_YET_VERIFIED</h2>
                <p>{safe_reason}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_evidence_grid(evidence, verification_date):
    """
    Agent evidence items use keys:
        claim, tool, source_url, source_title, verification_state
    All dynamic fields are HTML-escaped before interpolation.

    FIX: uses st.html() instead of st.markdown(..., unsafe_allow_html=True)
    so nested <div> tags render as HTML rather than literal text.
    """

    safe_verification_date = esc(verification_date)

    cards_html = ""

    if not evidence:
        # Fallback when agent returned no evidence items
        cards_html = f"""
        <div class="evidence-card">
            <div class="evidence-title">📄 Source Document</div>
            <div class="evidence-value">No verified evidence returned</div>
        </div>

        <div class="evidence-card">
            <div class="evidence-title">📖 Page</div>
            <div class="evidence-value">—</div>
        </div>

        <div class="evidence-card">
            <div class="evidence-title">🔗 Source URL</div>
            <div class="evidence-value">—</div>
        </div>

        <div class="evidence-card">
            <div class="evidence-title">📅 Verification Date</div>
            <div class="evidence-value">{safe_verification_date}</div>
        </div>
        """
    else:
        for item in evidence:
            if not isinstance(item, dict):
                # Last-resort: render anything as a plain string card
                cards_html += f"""
                <div class="evidence-card">
                    <div class="evidence-title">📄 Evidence</div>
                    <div class="evidence-value">{esc(item)}</div>
                </div>
                """
                continue

            claim = esc(item.get("claim", "") or "")
            tool = esc(item.get("tool", "") or "—")
            source_url_raw = item.get("source_url") or ""
            source_url = esc(source_url_raw)
            source_title = esc(item.get("source_title") or "Evidence")
            verification_state = esc(
                item.get("verification_state") or "UNKNOWN"
            )

            if source_url_raw:
                url_html = (
                    f'<a href="{source_url}" target="_blank" '
                    f'style="color:#2563eb; word-break:break-all;">'
                    f'{source_url}</a>'
                )
            else:
                url_html = "Not provided"

            state_color = "#16a34a"
            state_upper = str(verification_state).upper()
            if state_upper == "UNVERIFIED":
                state_color = "#dc2626"
            elif state_upper == "PARTIAL" or state_upper == "PENDING":
                state_color = "#d97706"

            cards_html += f"""
            <div class="evidence-card">
                <div class="evidence-title">📄 {source_title}</div>
                <div class="evidence-value">{claim}</div>
                <div class="evidence-value" style="font-size:0.85rem;margin-top:8px;">
                    <b>Tool:</b> {tool}<br>
                    <b>Source:</b> {url_html}<br>
                    <b>Verification:</b>
                    <span style="color:{state_color};font-weight:700;">
                        {state_upper}
                    </span><br>
                    <b>Verified:</b> {safe_verification_date}
                </div>
            </div>
            """

    # FIX: st.html() instead of st.markdown(..., unsafe_allow_html=True)
    st.html(
        f"""
        <div class="evidence-grid">
            {cards_html}
        </div>
        """
    )


# =========================================================
# 01 — HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧭 Rahbar AI</h1>
        <p>
            Intelligent university admission guidance.
            Enter your academic profile and ask Rahbar about
            universities, programmes, merit, deadlines and eligibility.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 02 — STUDENT PROFILE
# =========================================================

st.markdown(
    '<div class="section-title">01 — Student Profile</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">Required information for the admission agent.</div>',
    unsafe_allow_html=True
)

row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    university = st.selectbox(
        "University",
        ["NUST", "FAST", "COMSATS"]
    )

with row1_col2:
    program = st.selectbox(
        "Program",
        [
            "BS Computer Science",
            "BS Software Engineering",
            "BS Artificial Intelligence",
            "BS Data Science",
            "BS Electrical Engineering",
            "Other"
        ]
    )

with row1_col3:
    campus = st.text_input(
        "Campus (Optional)",
        placeholder="e.g. Islamabad"
    )

row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    cycle = st.text_input(
        "Admission Cycle",
        value="2026",
        placeholder="e.g. 2026"
    )

with row2_col2:
    part2_status = st.radio(
        "Part-II Result Status",
        ["Pending", "Declared", "Not applicable"],
        horizontal=True
    )

with row2_col3:
    ssc_marks = st.number_input(
        "SSC Marks (%)",
        min_value=0.0,
        max_value=100.0,
        value=80.0,
        step=0.1
    )

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    hssc_marks = st.number_input(
        "HSSC Marks (%)",
        min_value=0.0,
        max_value=100.0,
        value=75.0,
        step=0.1
    )

with row3_col2:
    hssc_group = st.selectbox(
        "HSSC Group",
        [
            "Pre-Engineering",
            "Pre-Medical",
            "Computer Science",
            "General Science",
            "Commerce",
            "Arts",
            "Other"
        ]
    )

entry_test = st.number_input(
    "Entry Test Score (%)",
    min_value=0.0,
    max_value=100.0,
    value=70.0,
    step=0.1
)


# =========================================================
# 02 — QUERY
# =========================================================

st.markdown(
    '<div class="section-title">02 — Ask Your Question</div>',
    unsafe_allow_html=True
)

query = st.text_area(
    "Question",
    placeholder="Example: Am I eligible for NUST BSCS in 2026?",
    height=120,
    label_visibility="collapsed"
)


# =========================================================
# 03 — GET GUIDANCE
# =========================================================

st.markdown(
    '<div class="section-title">03 — Get Guidance</div>',
    unsafe_allow_html=True
)

ask = st.button(
    "🚀 Ask Rahbar AI",
    use_container_width=True
)


# =========================================================
# PROCESS QUESTION
# =========================================================

if ask:

    if not query.strip():

        st.warning("Please enter your question first.")
        st.session_state.asked = False

    else:

        st.session_state.asked = True
        st.session_state.show_calculation = is_calculation_question(query)

        # -------------------------------------------------
        # Build the student profile dict from form fields
        # -------------------------------------------------
        profile = build_student_profile(
            university=university,
            program=program,
            campus=campus,
            cycle=cycle,
            part2_status=part2_status,
            ssc_marks=ssc_marks,
            hssc_marks=hssc_marks,
            hssc_group=hssc_group,
            entry_test=entry_test,
        )

        # -------------------------------------------------
        # Call the real agent
        # -------------------------------------------------
        response = None
        agent_error = ""

        if not AGENT_AVAILABLE:
            agent_error = f"Agent import failed: {AGENT_IMPORT_ERROR}"

        else:
            try:
                response = run_agent(query, profile)
            except Exception as e:
                agent_error = f"Agent execution error: {e}"
                response = None

        # -------------------------------------------------
        # Normalize response into session state
        # -------------------------------------------------
        if response is None:
            st.session_state.decision = "NOT_YET_VERIFIED"
            st.session_state.reason = (
                "Rahbar could not complete this request. "
                + (agent_error or "No response was returned by the agent.")
            )
            st.session_state.trace_steps = []
            st.session_state.evidence = []
            st.session_state.actions = []
            st.session_state.aggregate_data = None

        else:
            # Agent uses `status` and `decision_reason`,
            # not `decision` and `reason`. Read both defensively
            # so either shape works.
            decision = (
                _get(response, "status", None)
                or _get(response, "decision", None)
                or "NOT_YET_VERIFIED"
            )

            reason = (
                _get(response, "decision_reason", None)
                or _get(response, "reason", None)
                or ""
            )

            evidence = _get(response, "evidence", []) or []
            actions = _get(response, "actions", []) or []
            trace = _get(response, "agent_trace", []) or []

            st.session_state.decision = decision
            st.session_state.reason = reason
            st.session_state.evidence = evidence
            st.session_state.actions = actions
            st.session_state.trace_steps = trace

            # rules_engine is authoritative; local formula is the
            # only fallback. No LLM-derived numbers.
            st.session_state.aggregate_data = compute_aggregate(
                profile=profile,
                entry_test=entry_test,
                ssc_marks=ssc_marks,
                hssc_marks=hssc_marks,
            )


# =========================================================
# RESULTS
# =========================================================

if st.session_state.asked:

    # =====================================================
    # 04 — DECISION
    # =====================================================

    st.markdown(
        '<div class="section-title">04 — Decision</div>',
        unsafe_allow_html=True
    )

    render_decision(
        st.session_state.decision,
        st.session_state.reason
    )


    # =====================================================
    # 05 — AGGREGATE CALCULATION
    # =====================================================

    if st.session_state.aggregate_data:

        st.markdown(
            '<div class="section-title">05 — Aggregate Calculation</div>',
            unsafe_allow_html=True
        )

        agg = st.session_state.aggregate_data
        aggregate = agg.get("aggregate", 0.0) or 0.0
        entry_contribution = agg.get("entry_test_contribution", 0.0) or 0.0
        academic_contribution = agg.get("academic_contribution", 0.0) or 0.0

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">
                        {aggregate:.2f}%
                    </div>
                    <div class="metric-label">
                        Overall Aggregate
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">
                        {entry_contribution:.2f}%
                    </div>
                    <div class="metric-label">
                        Entry Test Contribution
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">
                        {academic_contribution:.2f}%
                    </div>
                    <div class="metric-label">
                        Academic Contribution
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # FIX: st.html() instead of st.markdown(..., unsafe_allow_html=True)
        st.html(
            f"""
            <div class="card">
                <b>Formula</b>

                <p>
                    Aggregate =
                    (Entry Test × 75%) +
                    (SSC × 10%) +
                    (HSSC × 15%)
                </p>

                <b>Calculation</b>

                <p>
                    ({entry_test:.2f} × 0.75)
                    +
                    ({ssc_marks:.2f} × 0.10)
                    +
                    ({hssc_marks:.2f} × 0.15)
                    =
                    <b>{aggregate:.2f}%</b>
                </p>

                <span style="color:#64748b;">
                    Aggregate is computed from the student's
                    academic profile using the university's
                    merit formula.
                </span>
            </div>
            """
        )


    # =====================================================
    # 06 — EVIDENCE
    # =====================================================

    st.markdown(
        '<div class="section-title">06 — Evidence</div>',
        unsafe_allow_html=True
    )

    verification_date = date.today().strftime("%d %B %Y")

    render_evidence_grid(
        st.session_state.evidence,
        verification_date
    )


    # =====================================================
    # 07 — ACTIONS
    # =====================================================

    st.markdown(
        '<div class="section-title">07 — Recommended Actions</div>',
        unsafe_allow_html=True
    )

    actions_list = st.session_state.actions or [
        {
            "action": "Verify the answer against the university's official admission source.",
            "why": "Ensure the guidance matches the current admission policy.",
            "priority": "HIGH",
        },
        {
            "action": "Confirm the selected programme and campus requirements.",
            "why": "Programme-specific criteria can vary by campus.",
            "priority": "MEDIUM",
        },
        {
            "action": "Check the relevant admission deadline.",
            "why": "Missing the deadline invalidates the application.",
            "priority": "HIGH",
        },
        {
            "action": "Keep your academic documents ready for the application.",
            "why": "Fast submission once the portal opens.",
            "priority": "MEDIUM",
        },
    ]

    for i, action in enumerate(actions_list, start=1):

        if isinstance(action, dict):
            action_text = esc(action.get("action", "") or str(action))
            why_text = esc(action.get("why", "") or "")
            priority = esc(
                (action.get("priority", "") or "").upper()
            )

            priority_color = "#2563eb"
            priority_raw = (action.get("priority", "") or "").upper()
            if priority_raw == "HIGH":
                priority_color = "#dc2626"
            elif priority_raw == "MEDIUM":
                priority_color = "#d97706"
            elif priority_raw == "LOW":
                priority_color = "#16a34a"

            priority_html = ""
            if priority:
                priority_html = (
                    f'<span style="background:{priority_color};'
                    f'color:white;padding:2px 8px;border-radius:8px;'
                    f'font-size:0.7rem;font-weight:800;'
                    f'margin-left:8px;">{priority}</span>'
                )

            why_html = ""
            if why_text:
                why_html = (
                    f'<div style="color:#64748b;font-size:0.88rem;'
                    f'margin-top:6px;margin-left:40px;">{why_text}</div>'
                )

            st.markdown(
                f"""
                <div class="action">
                    <div>
                        <span class="action-number">{i}</span>
                        <b>{action_text}</b>{priority_html}
                    </div>
                    {why_html}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                f"""
                <div class="action">
                    <span class="action-number">{i}</span>
                    {esc(action)}
                </div>
                """,
                unsafe_allow_html=True
            )


    # =====================================================
    # 08 — LIMITATIONS
    # =====================================================

    st.markdown(
        '<div class="section-title">08 — Limitations</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Rahbar will only return a final YES, NO or CONDITIONAL "
        "decision when verified evidence is available. "
        "Unverified, future or unavailable information is marked "
        "NOT_YET_VERIFIED."
    )


    # =====================================================
    # 09 — AGENT TRACE
    # =====================================================

    st.markdown(
        '<div class="section-title">09 — Agent Trace</div>',
        unsafe_allow_html=True
    )

    trace_html = ""

    for index, step in enumerate(
        st.session_state.trace_steps,
        start=1
    ):

        if isinstance(step, dict):
            event = esc(step.get("event", "step"))
            tool = esc(step.get("tool", "") or "")
            summary = esc(step.get("summary", "") or "")
            ts = esc(step.get("ts", "") or "")

            ts_html = ""
            if ts:
                ts_html = (
                    f'<span class="trace-muted">'
                    f'[{ts}]</span> '
                )

            tool_html = ""
            if tool:
                tool_html = (
                    f'<span class="trace-muted">'
                    f'(tool: {tool})</span> '
                )

            summary_html = ""
            if summary:
                summary_html = (
                    f'<span class="trace-muted">'
                    f'— {summary}</span>'
                )

            trace_html += f"""
            <div class="trace-step">
                {ts_html}Step {index} — {event} {tool_html}{summary_html}
            </div>
            """

        else:
            trace_html += f"""
            <div class="trace-step">
                Step {index} — {esc(step)}
            </div>
            """

    if not trace_html:
        trace_html = (
            '<div class="trace-muted">No trace available.</div>'
        )

    # FIX: st.html() instead of st.markdown(..., unsafe_allow_html=True)
    st.html(
        f"""
        <div class="trace">

            <div class="trace-muted">
                $ rahbar-agent --run
            </div>

            <br>

            {trace_html}

            <br>

            <div class="trace-muted">
                $ status: COMPLETE
            </div>

        </div>
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        padding:2rem 0;
        font-size:0.85rem;
    ">
        🧭 <b>Rahbar AI</b> · Student Admission Guidance
    </div>
    """,
    unsafe_allow_html=True
)