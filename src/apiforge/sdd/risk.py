"""Risk-adaptive SDD: deterministic change classification and minimum SDD profile.

A change is classified from explicit signals only — a contract diff verdict,
the touched paths and the change description — never from a model call. Missing
signals never classify below ``medium``; the unresolved state is reported.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from apiforge.contracts.economy import RiskClass, RiskClassification

RISK_UNRESOLVED = "AF-SDD-RISK-UNRESOLVED"
RANK: dict[RiskClass, int] = {"micro": 0, "low": 1, "medium": 2, "high": 3}
PROFILE_RANK: dict[str, int] = {
    "micro": 0,
    "quick": 1,
    "standard": 2,
    "critical": 3,
    "migration": 3,
}
REQUIRED_PROFILE: dict[RiskClass, str] = {
    "micro": "micro",
    "low": "quick",
    "medium": "standard",
    "high": "critical",
}

_HIGH_WORDS = re.compile(
    r"\b(auth\w*|security|secret|credential|token|payment\w*|breaking|migrat\w*|"
    r"cross-repo|consistency|pii|encryption|permission\w*)\b",
    re.IGNORECASE,
)
_MEDIUM_WORDS = re.compile(
    r"\b(contract|schema|dependenc\w*|version\w*|endpoint|field|enum|openapi|proto)\b",
    re.IGNORECASE,
)
_MICRO_WORDS = re.compile(r"\b(doc\w*|typo|readme|comment|metadata|description)\b", re.IGNORECASE)
_HIGH_PATHS = re.compile(r"(auth|security|payment|migrations?|secrets?|iam|policy)", re.IGNORECASE)
_CONTRACT_PATHS = re.compile(
    r"(openapi|swagger|\.proto$|asyncapi|(^|/)contracts?/|(^|/)schemas?/|pom\.xml$|requirements.*\.txt$|pyproject\.toml$|go\.mod$|package\.json$)",
    re.IGNORECASE,
)
_DOC_PATHS = re.compile(r"(\.md$|\.rst$|\.txt$|^docs/|/docs/)", re.IGNORECASE)


def classify(
    *,
    description: str = "",
    paths: Sequence[str] = (),
    contract_verdict: str | None = None,
    repositories: int = 1,
) -> RiskClassification:
    signals: list[str] = []
    level: RiskClass | None = None

    def raise_to(candidate: RiskClass, signal: str) -> None:
        nonlocal level
        signals.append(signal)
        if level is None or RANK[candidate] > RANK[level]:
            level = candidate

    if contract_verdict == "breaking":
        raise_to("high", "contract:breaking")
    elif contract_verdict in {"review", "inconclusive"}:
        raise_to("medium", f"contract:{contract_verdict}")
    elif contract_verdict == "compatible":
        raise_to("low", "contract:compatible")
    if repositories > 1:
        raise_to("high", f"cross-repo:{repositories}")
    for word in sorted({match.lower() for match in _HIGH_WORDS.findall(description)}):
        raise_to("high", f"keyword:{word}")
    for word in sorted({match.lower() for match in _MEDIUM_WORDS.findall(description)}):
        raise_to("medium", f"keyword:{word}")
    normalized = [Path(item).as_posix() for item in paths]
    for path in normalized:
        if _HIGH_PATHS.search(path):
            raise_to("high", f"path:{path}")
        elif _CONTRACT_PATHS.search(path):
            raise_to("medium", f"path:{path}")
        elif not _DOC_PATHS.search(path):
            raise_to("low", f"path:{path}")
    only_docs = bool(normalized) and all(_DOC_PATHS.search(path) for path in normalized)
    if level is None and (only_docs or _MICRO_WORDS.search(description)):
        signals.append("docs-only" if only_docs else "keyword:docs")
        level = "micro"
    unresolved: tuple[str, ...] = ()
    if level is None:
        level = "medium"
        unresolved = (f"{RISK_UNRESOLVED}: no classifying signal; defaulted to medium",)
    profile = REQUIRED_PROFILE[level]
    if level == "high" and repositories > 1:
        profile = "migration"
    return RiskClassification(
        risk_class=level,
        sdd_profile=profile,
        signals=tuple(signals),
        unresolved=unresolved,
    )


def profile_below_risk(profile: str, risk_class: str) -> bool:
    required = REQUIRED_PROFILE.get(risk_class)  # type: ignore[call-overload]
    if required is None or profile not in PROFILE_RANK:
        return False
    return PROFILE_RANK[profile] < PROFILE_RANK[required]


def write_classification(feature_dir: Path, result: RiskClassification) -> Path:
    path = Path(feature_dir) / "intent.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} has no frontmatter")
    end = text.index("\n---", 4)
    lines = [
        line
        for line in text[4:end].splitlines()
        if not line.startswith(("risk_class:", "risk_signals:"))
    ]
    lines.append(f"risk_class: {result.risk_class}")
    lines.append("risk_signals: [" + ", ".join(result.signals) + "]")
    path.write_text("---\n" + "\n".join(lines) + text[end:], encoding="utf-8", newline="\n")
    return path


__all__ = [
    "PROFILE_RANK",
    "RANK",
    "REQUIRED_PROFILE",
    "classify",
    "profile_below_risk",
    "write_classification",
]
