"""§37 semantic retrieval — optional adapter, never a requirement.

The shipped adapter is a deterministic hash-embedding: terms are folded into
a fixed bucket vector and compared by cosine. No vector DB, no network, no
provider call — a caller may declare a stronger adapter by passing any object
implementing :class:`SemanticAdapter`.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

_WORD = re.compile(r"[^\W_][\w-]*")
_BUCKETS = 256


class SemanticAdapter(Protocol):
    """Deterministic embedding similarity; implementations never call providers."""

    def score(self, query_terms: tuple[str, ...], text: str) -> float:
        """Cosine-like similarity in ``[0, 1]``."""
        ...


class HashEmbeddingAdapter:
    """Local adapter: term -> hash bucket; cosine over bucket vectors."""

    def _vector(self, terms: tuple[str, ...]) -> list[float]:
        vector = [0.0] * _BUCKETS
        for term in terms:
            digest = hashlib.sha256(term.encode("utf-8")).digest()
            vector[digest[0]] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector

    def score(self, query_terms: tuple[str, ...], text: str) -> float:
        text_terms = tuple(term.lower() for term in _WORD.findall(text))
        if not query_terms or not text_terms:
            return 0.0
        left = self._vector(tuple(term.lower() for term in query_terms))
        right = self._vector(text_terms)
        return round(sum(a * b for a, b in zip(left, right, strict=True)), 6)


def load_semantic_adapter(declared: SemanticAdapter | None = None) -> SemanticAdapter | None:
    """The semantic layer exists only when declared — callers may pass None."""
    return declared if declared is not None else HashEmbeddingAdapter()


__all__ = ["HashEmbeddingAdapter", "SemanticAdapter", "load_semantic_adapter"]
