"""Live evidence only when needed (§97): classify the question before paying for it.

A question about the artifact ("was the field removed?") is answered from the
local OpenAPI/code and never reaches AWS, Datadog, CloudWatch or GitHub. A
question about a runtime effect ("did this cause errors in production?") may
use ``live_read_only`` evidence and must bring a read-only receipt.
``live_mutation`` is refused (§98); offline runs fall back to fixtures.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_resume import LiveEvidenceDecision

TRIGGERS_FILE = Path(__file__).resolve().parents[1] / "rules" / "live_evidence_triggers.yaml"
_MODES = ("static", "fixture", "live_read_only", "live_mutation")


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


@lru_cache(maxsize=4)
def load_triggers(path: str = str(TRIGGERS_FILE)) -> dict[str, tuple[dict[str, Any], ...]]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise _refusal(
            "AF-EVIDENCE-TRIGGERS-INVALID",
            f"{path}: {exc}",
            "rules",
            "restore rules/live_evidence_triggers.yaml",
        ) from exc
    out: dict[str, tuple[dict[str, Any], ...]] = {}
    for kind in ("runtime", "static"):
        groups = raw.get(kind)
        if not isinstance(groups, list) or not all(
            isinstance(group, dict) and isinstance(group.get("terms"), list) for group in groups
        ):
            raise _refusal(
                "AF-EVIDENCE-TRIGGERS-INVALID",
                f"{path}: '{kind}' must be a list of groups with 'terms'",
                "rules",
                "restore rules/live_evidence_triggers.yaml",
            )
        out[kind] = tuple(groups)
    return out


def _hits(text: str, groups: tuple[dict[str, Any], ...]) -> tuple[list[str], list[str]]:
    terms: list[str] = []
    sources: list[str] = []
    for group in groups:
        matched = [str(term) for term in group["terms"] if str(term).lower() in text]
        if matched:
            terms.extend(matched)
            sources.extend(str(item) for item in group.get("sources", ()))
    return sorted(set(terms)), list(dict.fromkeys(sources))


def gate(
    question: str, *, requested: str | None = None, offline: bool = False
) -> LiveEvidenceDecision:
    """Decide the cheapest evidence mode that can answer ``question``."""
    if not question.strip():
        raise _refusal(
            "AF-EVIDENCE-QUESTION-EMPTY", "question is empty", "question", "pass the question"
        )
    if requested is not None and requested not in _MODES:
        raise _refusal(
            "AF-EVIDENCE-MODE-INVALID",
            f"mode {requested!r} is not one of {', '.join(_MODES)}",
            "mode",
            "use static|fixture|live_read_only",
        )
    if requested == "live_mutation":
        raise _refusal(
            "AF-EVIDENCE-MUTATION-REFUSED",
            "live_mutation is never granted to answer a question; read-only evidence comes first",
            "mode",
            "use live_read_only; a mutation needs a separate approved change",
        )
    triggers = load_triggers()
    text = question.lower()
    runtime_terms, sources = _hits(text, triggers["runtime"])
    static_terms, _ = _hits(text, triggers["static"])
    reasons: list[str] = []
    if runtime_terms:
        question_class = "runtime"
        reasons.append("question names a runtime effect: " + ", ".join(runtime_terms))
        if static_terms:
            reasons.append("answer the static part locally before reading runtime evidence")
        if offline:
            mode, live = "fixture", False
            reasons.append("offline: use recorded fixtures; without them the answer is unresolved")
        else:
            mode, live = "live_read_only", True
    elif static_terms:
        question_class, mode, live = "static", "static", False
        reasons.append("local artifacts answer this question: " + ", ".join(static_terms))
        if requested == "live_read_only":
            reasons.append("live evidence requested but not justified for a static question")
    else:
        question_class, mode, live = "ambiguous", "static", False
        reasons.append("no runtime term; answer from local artifacts first")
    return LiveEvidenceDecision(
        question=question,
        question_class=question_class,  # type: ignore[arg-type]
        mode=mode,  # type: ignore[arg-type]
        live_allowed=live,
        runtime_terms=tuple(runtime_terms),
        static_terms=tuple(static_terms),
        suggested_sources=tuple(sources) if question_class == "runtime" else (),
        requires_receipt=question_class == "runtime",
        escalate_if_unanswered=question_class == "ambiguous",
        reasons=tuple(reasons),
    )


__all__ = ["gate", "load_triggers"]
