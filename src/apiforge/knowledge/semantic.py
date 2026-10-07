"""§37 semantic retrieval — optional adapter, never a requirement.

The shipped adapter is deterministic hash-feature similarity: terms are folded
into a fixed bucket vector and compared by cosine-like overlap. It is not a
semantic embedding. No vector DB, network or provider call; callers may
declare stronger adapters through :class:`SemanticAdapter`.
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

    def candidates(
        self, query_terms: tuple[str, ...], documents: tuple[tuple[str, str], ...]
    ) -> tuple[tuple[str, float], ...]:
        """Return non-lexical candidates as ``(document_id, score)`` rows."""
        ...


class HashFeatureSimilarityAdapter:
    """Local lexical-feature adapter: term -> hash bucket; cosine-like score."""

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

    def candidates(
        self, query_terms: tuple[str, ...], documents: tuple[tuple[str, str], ...]
    ) -> tuple[tuple[str, float], ...]:
        scored = ((ref, self.score(query_terms, text)) for ref, text in documents)
        return tuple((ref, score) for ref, score in scored if score > 0.0)


def load_semantic_adapter(declared: SemanticAdapter | None = None) -> SemanticAdapter | None:
    """The semantic layer exists only when declared — callers may pass None."""
    return declared if declared is not None else HashFeatureSimilarityAdapter()


HashEmbeddingAdapter = HashFeatureSimilarityAdapter

__all__ = [
    "HashEmbeddingAdapter",
    "HashFeatureSimilarityAdapter",
    "SemanticAdapter",
    "load_semantic_adapter",
]
