"""
rag.py — Retrieval module for Rahbar AI.

Semantic retrieval using Sentence Transformers + FAISS.

FROZEN INTERFACE:
    search(query, university=None, cycle=None, section=None,
           program=None, k=5) -> list[dict]

RAG retrieves evidence only. It never makes admission decisions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).parent

INDEX_PATH = BASE_DIR / "faiss.index"
METADATA_PATH = BASE_DIR / "metadata.json"

MODEL_NAME = "all-MiniLM-L6-v2"

# Minimum semantic similarity required to return evidence.
SIMILARITY_THRESHOLD = 0.20

_INDEX = None
_METADATA: list[dict] = []
_MODEL = None


def _load() -> None:
    """Load FAISS index, metadata and embedding model."""
    global _INDEX, _METADATA, _MODEL

    try:
        if not INDEX_PATH.exists() or not METADATA_PATH.exists():
            return

        _INDEX = faiss.read_index(str(INDEX_PATH))

        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            _METADATA = data

        _MODEL = SentenceTransformer(MODEL_NAME)

    except Exception:
        _INDEX = None
        _METADATA = []
        _MODEL = None


def _norm(value) -> str:
    return str(value or "").strip().lower()


def _matches_filters(
    metadata: dict,
    university: Optional[str],
    cycle: Optional[str],
    section: Optional[str],
    program: Optional[str],
) -> bool:
    """Apply hard metadata filters."""
    if university and _norm(metadata.get("university")) != _norm(university):
        return False

    if cycle and _norm(metadata.get("cycle")) != _norm(cycle):
        return False

    if section and _norm(metadata.get("section")) != _norm(section):
        return False

    if program and _norm(metadata.get("program")) != _norm(program):
        return False

    return True


def _section_boost(query: str, section: str) -> int:
    """
    Deterministic section booster.

    Semantic search alone sometimes ranks a topically related chunk
    above the specifically relevant one (e.g. Part-I Application can
    outrank Eligibility for an eligibility question). This function
    nudges the correct section to the top for keyword-heavy queries.

    Returns a non-negative integer added to the chunk's score.
    """
    q = _norm(query)
    s = _norm(section)

    # Eligibility-style questions
    if any(w in q for w in ("eligib", "requirement", "qualify", "can i", "am i")):
        if s in ("eligibility", "eligible groups"):
            return 3

    # Deadline-style questions
    if any(w in q for w in ("deadline", "last date", "open", "closed", "due")):
        if s == "deadline":
            return 3

    # Merit-formula questions
    if any(w in q for w in ("formula", "merit", "aggregate", "calculate")):
        if s in ("merit formula", "formula"):
            return 3

    # Documents-style questions
    if any(w in q for w in ("document", "documents", "certificate", "cnic")):
        if s in ("documents", "document"):
            return 3

    # Part-I application style questions
    if "part 1" in q or "part-i" in q or "part i" in q:
        if s == "part-i application":
            return 3

    return 0


def search(
    query: str,
    university: Optional[str] = None,
    cycle: Optional[str] = None,
    section: Optional[str] = None,
    program: Optional[str] = None,
    k: int = 5,
) -> list[dict]:
    """
    Search verified evidence using semantic similarity + section boost
    + hard metadata filters.
    """

    try:
        if not query or not str(query).strip():
            return []

        if _INDEX is None or not _METADATA or _MODEL is None:
            _load()

        if _INDEX is None or not _METADATA or _MODEL is None:
            return []

        k = max(0, int(k))

        if k == 0:
            return []

        # Encode query.
        query_vector = _MODEL.encode(
            [str(query)],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        # Search all vectors so metadata filters can be applied safely.
        scores, indices = _INDEX.search(
            query_vector,
            len(_METADATA),
        )

        results = []

        for score, vector_id in zip(scores[0], indices[0]):

            if vector_id < 0 or vector_id >= len(_METADATA):
                continue

            if float(score) < SIMILARITY_THRESHOLD:
                continue

            item = _METADATA[vector_id]

            metadata = item.get("metadata", {})

            if not _matches_filters(
                metadata,
                university,
                cycle,
                section,
                program,
            ):
                continue

            section_name = metadata.get("section", "")
            boost = _section_boost(query, section_name)
            effective_score = float(score) + boost

            results.append(
                {
                    "text": item.get("text", ""),
                    "metadata": {
                        "university": metadata.get("university", ""),
                        "cycle": metadata.get("cycle", ""),
                        "program": metadata.get("program", ""),
                        "section": section_name,
                        "source_url": metadata.get("source_url", ""),
                        "verification_state": metadata.get(
                            "verification_state", ""
                        ),
                    },
                    "score": effective_score,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

    except Exception:
        return []


_load()