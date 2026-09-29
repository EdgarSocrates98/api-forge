"""Deterministic proxy-router eval over agent descriptions.

Hosts route with a model over each agent's description; this eval cannot call
a model, so it ranks agents lexically (idf-weighted token overlap: description
x2, "When you enter" x1, "When not to enter" x-1). It measures what the roster
controls — distinct, trigger-rich descriptions — not the host router itself.
Predictions pass through the alias table so a pre-consolidation roster is
scored against the post-consolidation golden labels.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from apiforge.contracts.agents import (
    AgentRoutingCase,
    AgentRoutingMiss,
    AgentRoutingReport,
    AgentSource,
)
from apiforge.contracts.base import ContractError
from apiforge.dispatch.agent_source import load_roster, sections
from apiforge.dispatch.aliases import AliasTable, load_table

CORPUS = Path("evals") / "corpus" / "agent-routing" / "cases.json"
PROTECTED = frozenset({"api-adversarial-critic", "api-debate-referee", "api-verifier"})
_ENTER = ("When you enter", "Quando você entra")
_NOT_ENTER = ("When not to enter", "Quando NÃO entra", "Quando não entra")
_STOP = frozenset(
    [
        "the",
        "and",
        "for",
        "this",
        "that",
        "with",
        "from",
        "are",
        "was",
        "were",
        "into",
        "what",
        "when",
        "how",
        "does",
        "which",
        "should",
        "our",
        "you",
        "your",
        "its",
        "has",
        "have",
        "can",
        "not",
        "but",
        "all",
        "any",
        "use",
        "via",
        "per",
        "about",
        "before",
        "after",
        "then",
        "than",
    ]
)
_TOKEN = re.compile(r"[a-z0-9à-ÿ]+")


def tokens(text: str) -> set[str]:
    return {word for word in _TOKEN.findall(text.lower()) if len(word) > 2 and word not in _STOP}


def _section(agent: AgentSource, titles: tuple[str, ...]) -> str:
    found = sections(agent.body)
    return next((found[title] for title in titles if title in found), "")


class ProxyRouter:
    def __init__(self, roster: tuple[AgentSource, ...]) -> None:
        self.docs = {
            agent.name: (
                tokens(agent.description),
                tokens(_section(agent, _ENTER)),
                tokens(_section(agent, _NOT_ENTER)),
            )
            for agent in roster
        }
        frequency: Counter[str] = Counter()
        for description, enter, _ in self.docs.values():
            frequency.update(description | enter)
        total = max(1, len(self.docs))
        self.idf = {
            word: math.log((1 + total) / (1 + count)) + 1 for word, count in frequency.items()
        }

    def rank(self, question: str) -> list[str]:
        words = tokens(question)
        scores: list[tuple[float, str]] = []
        for name, (description, enter, not_enter) in self.docs.items():
            score = sum(
                self.idf.get(word, 0.0)
                * (2 * (word in description) + (word in enter) - (word in not_enter))
                for word in words
            )
            scores.append((-round(score, 6), name))
        return [name for _, name in sorted(scores)]


def _grams(text: str, size: int = 4) -> set[tuple[str, ...]]:
    words = _TOKEN.findall(text.lower())
    return {tuple(words[index : index + size]) for index in range(len(words) - size + 1)}


def leakage(roster: tuple[AgentSource, ...], cases: tuple[AgentRoutingCase, ...]) -> float:
    """Share of cases that copy a 4-word sequence from their expected agent's routing text."""
    docs = {
        agent.name: _grams(f"{agent.description} {_section(agent, _ENTER)}") for agent in roster
    }
    leaked = sum(1 for case in cases if _grams(case.question) & docs.get(case.expected, set()))
    return round(leaked / len(cases), 4) if cases else 0.0


def load_cases(path: Path) -> tuple[AgentRoutingCase, ...]:
    if not path.is_file():
        raise ContractError("AF-EVAL-AGENT-ROUTING", f"{path} is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(AgentRoutingCase.model_validate(item) for item in data.get("cases", ()))


def evaluate(
    roster: tuple[AgentSource, ...],
    cases: tuple[AgentRoutingCase, ...],
    table: AliasTable,
) -> AgentRoutingReport:
    router = ProxyRouter(roster)

    def mapped(name: str) -> str:
        return table.aliases.get(name, name)

    hits1 = hits3 = 0
    family_total: Counter[str] = Counter()
    family_hits: Counter[str] = Counter()
    misses: list[AgentRoutingMiss] = []
    protected: list[str] = []
    for case in cases:
        ranked = [mapped(name) for name in router.rank(case.question)]
        top3: list[str] = []
        for name in ranked:
            if name not in top3:
                top3.append(name)
            if len(top3) == 3:
                break
        predicted = top3[0] if top3 else ""
        family_total[case.family] += 1
        if predicted == case.expected:
            hits1 += 1
            family_hits[case.family] += 1
        else:
            misses.append(
                AgentRoutingMiss(
                    id=case.id, expected=case.expected, predicted=predicted, top3=tuple(top3)
                )
            )
            if case.expected in PROTECTED or predicted in PROTECTED:
                protected.append(case.id)
        if case.expected in top3:
            hits3 += 1
    count = len(cases)
    by_family: dict[str, float] = defaultdict(float)
    for family, total in family_total.items():
        by_family[family] = round(family_hits[family] / total, 4)
    return AgentRoutingReport(
        cases=count,
        agents=len(roster),
        top1=round(hits1 / count, 4) if count else 0.0,
        top3=round(hits3 / count, 4) if count else 0.0,
        by_family=tuple(sorted(by_family.items())),
        protected_misroutes=tuple(protected),
        misses=tuple(misses),
        leakage_4gram=leakage(roster, cases),
        alias_mapping_applied=bool(table.aliases),
        limitations=(
            "lexical proxy of the host router; hosts route with a model over the same descriptions",
            "leakage_4gram is the share of cases sharing a 4-word sequence with the expected agent",
        ),
    )


def run(root: Path, cases_path: Path | None = None) -> AgentRoutingReport:
    root = Path(root)
    return evaluate(load_roster(root), load_cases(cases_path or root / CORPUS), load_table())


def compare(candidate: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    """Gate: top-1 and top-3 may not regress; protected-role misroutes may not grow."""

    def number(report: dict[str, object], key: str) -> float:
        value = report.get(key, 0.0)
        return float(value) if isinstance(value, int | float) else 0.0

    def protected(report: dict[str, object]) -> int:
        value = report.get("protected_misroutes", ())
        return len(value) if isinstance(value, list | tuple) else 0

    checks = {
        "top1": number(candidate, "top1") >= number(baseline, "top1"),
        "top3": number(candidate, "top3") >= number(baseline, "top3"),
        "protected_misroutes": protected(candidate) <= protected(baseline),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "baseline": {
            "top1": number(baseline, "top1"),
            "top3": number(baseline, "top3"),
            "protected_misroutes": protected(baseline),
        },
    }


__all__ = [
    "CORPUS",
    "PROTECTED",
    "ProxyRouter",
    "compare",
    "evaluate",
    "leakage",
    "load_cases",
    "run",
    "tokens",
]
