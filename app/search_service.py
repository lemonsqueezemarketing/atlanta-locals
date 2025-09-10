# search_service.py
from __future__ import annotations
import re
from typing import List, Dict, Set, Tuple

# -------- tokenization & synonyms (easy to evolve later) ---------------------

_WORD_RE = re.compile(r"[a-z0-9']+")

def _tokens(text: str) -> List[str]:
    if not text:
        return []
    return _WORD_RE.findall(text.lower())

# You can grow/tune this anytime; ML can replace/augment this later.
DEFAULT_SYNONYMS: Dict[str, Set[str]] = {
    "taco": {"taco", "tacos", "mexican"},
    "barber": {"barber", "barbershop", "fade", "hair"},
    "coffee": {"coffee", "cafe", "espresso"},
    "tea": {"tea", "teahouse"},
    "juice": {"juice", "smoothie"},
    "sake": {"sake", "bar"},
    "restaurant": {"restaurant", "food", "dining"},
}

def _expand_query_terms(q: str, synonyms: Dict[str, Set[str]] | None) -> Set[str]:
    base = set(_tokens(q))
    syn = synonyms or DEFAULT_SYNONYMS
    expanded: Set[str] = set()
    for t in base:
        expanded |= syn.get(t, {t})
    return expanded or base

# -------- scoring ------------------------------------------------------------

def _score_place(place: dict, terms: Set[str]) -> int:
    """
    Very basic scoring you can iterate on:
      title > tags/categories > address > slug
    """
    title = " ".join(_tokens(place.get("title", "")))
    cats  = " ".join(_tokens(" ".join(place.get("categories") or [])))
    tags  = " ".join(_tokens(" ".join(place.get("tags") or [])))   # optional field
    addr  = " ".join(_tokens(place.get("address", "")))
    slug  = " ".join(_tokens(place.get("slug", "")))

    score = 0
    for t in terms:
        if t in title: score += 3
        if t in tags:  score += 2
        if t in cats:  score += 2
        if t in addr:  score += 1
        if t in slug:  score += 1
    return score

# -------- public API ---------------------------------------------------------

def search_places(
    q: str,
    places: List[dict],
    *,
    synonyms: Dict[str, Set[str]] | None = None,
    show_all_on_empty: bool = False,
) -> List[dict]:
    """
    Returns a filtered/sorted list of places. Keep this as your single
    search entry point so you can swap in BM25/embeddings/ML later.
    """
    q = (q or "").strip()
    if not q:
        return places if show_all_on_empty else []

    terms = _expand_query_terms(q, synonyms)
    scored: List[Tuple[int, dict]] = []

    for p in places:
        s = _score_place(p, terms)
        if s > 0:
            scored.append((s, p))

    # Sort by score, then review_count, then rating (desc)
    scored.sort(
        key=lambda t: (t[0], t[1].get("review_count", 0), t[1].get("rating", 0)),
        reverse=True,
    )
    return [p for _, p in scored]
