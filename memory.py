"""
Short-term session memory for Rahbar AI.
Uses Streamlit session_state only.
No disk, no database, no cross-session persistence.
"""

import streamlit as st


_PROFILE_KEY = "student_profile"
_CONTEXT_KEY = "recent_context"


def _ensure_session() -> None:
    if _PROFILE_KEY not in st.session_state:
        st.session_state[_PROFILE_KEY] = {}
    if _CONTEXT_KEY not in st.session_state:
        st.session_state[_CONTEXT_KEY] = []


def get_student_profile() -> dict:
    _ensure_session()
    return dict(st.session_state[_PROFILE_KEY])


def update_student_profile(patch: dict) -> dict:
    _ensure_session()
    profile = dict(st.session_state[_PROFILE_KEY])
    profile.update({k: v for k, v in patch.items() if v is not None})
    st.session_state[_PROFILE_KEY] = profile
    return profile


def get_recent_context(n: int = 5) -> list[dict]:
    _ensure_session()
    return list(st.session_state[_CONTEXT_KEY][-n:])


def append_to_context(entry: dict) -> None:
    _ensure_session()
    ctx = list(st.session_state[_CONTEXT_KEY])
    ctx.append(entry)
    st.session_state[_CONTEXT_KEY] = ctx[-20:]


def clear_session_context() -> None:
    st.session_state[_PROFILE_KEY] = {}
    st.session_state[_CONTEXT_KEY] = []