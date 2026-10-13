"""Graph-quality eval: per rule x language precision/recall over the golden corpus.

Each case is one fixture file with the exact set of graph rules that must
fire on it (hand-written ground truth). Findings come from the real
extraction + catalog judge path. The run fails when precision, recall,
bounded false positives or corpus coverage miss ``thresholds.yaml``.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from apiforge.adapters.graph_.extract import extract_graph_access
from apiforge.contracts.base import ContractError
from apiforge.core.yaml import load_yaml_mapping
from apiforge.rules.fact_judge import judge_facts

GRAPH_RULES = ("AF-DATA-013",)
_RULE_PREFIX = "AF-GDB-"


class GraphQualityError(ContractError):
    def __init__(self, detail: str) -> None:
        super().__init__("AF-EVALS-INVALID", detail)
        self.field = "corpus"
        self.unlock = "restore evals/corpus/graph-quality (cases.json, thresholds.yaml, fixtures/)"


def _ratio(num: int, den: int) -> float:
    return round(num / den, 4) if den else 1.0


def _graph_rule(rule_id: str) -> bool:
    return rule_id in GRAPH_RULES or rule_id.startswith(_RULE_PREFIX)


def _fired_by_file(corpus: Path) -> dict[str, set[str]]:
    inventory = extract_graph_access(corpus)
    path_of = {fact.fact_id: fact.source.path for fact in inventory.facts}
    fired: dict[str, set[str]] = defaultdict(set)
    for finding in judge_facts(inventory.facts):
        if _graph_rule(finding.rule_id):
            fired[path_of[finding.evidence[0]]].add(finding.rule_id)
    return fired


def _load(corpus: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cases_path = corpus / "cases.json"
    thresholds_path = corpus / "thresholds.yaml"
    if not cases_path.is_file() or not thresholds_path.is_file():
        raise GraphQualityError(f"{corpus}: cases.json or thresholds.yaml missing")
    cases = json.loads(cases_path.read_text(encoding="utf-8")).get("cases") or []
    ids = [case["id"] for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise GraphQualityError(f"{cases_path}: empty or duplicated case ids")
    return cases, load_yaml_mapping(
        thresholds_path.read_text(encoding="utf-8"), source=str(thresholds_path)
    )


def run_graph_quality(corpus: Path) -> dict[str, Any]:
    """Score every case and compare against the declared thresholds."""
    corpus = Path(corpus)
    cases, thresholds = _load(corpus)
    support: dict[str, list[str]] = thresholds["support"]
    counts: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"tp": 0, "fp": 0, "fn": 0, "positive": 0, "negative": 0}
    )
    mismatches: list[dict[str, Any]] = []
    bounded_fp = 0
    fired_by_file = _fired_by_file(corpus)
    for case in cases:
        language = case["language"]
        expected = set(case["expect"])
        fired = fired_by_file.get(case["file"], set())
        for rule, languages in support.items():
            if language not in languages:
                continue
            row = counts[(rule, language)]
            row["positive" if rule in expected else "negative"] += 1
            if rule in expected and rule in fired:
                row["tp"] += 1
            elif rule in fired:
                row["fp"] += 1
                if rule == "AF-DATA-013":
                    bounded_fp += 1
            elif rule in expected:
                row["fn"] += 1
        if fired != expected:
            mismatches.append(
                {
                    "case": case["id"],
                    "missing": sorted(expected - fired),
                    "unexpected": sorted(fired - expected),
                }
            )
    rows = []
    language_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0})
    tp_all = fn_all = 0
    coverage_gaps: list[str] = []
    minimum = thresholds["min_cases_per_rule_language"]
    for (rule, language), row in sorted(counts.items()):
        language_totals[language]["tp"] += row["tp"]
        language_totals[language]["fp"] += row["fp"]
        tp_all += row["tp"]
        fn_all += row["fn"]
        if row["positive"] < minimum["positive"] or row["negative"] < minimum["negative"]:
            coverage_gaps.append(f"{rule}/{language}")
        rows.append(
            {
                "rule": rule,
                "language": language,
                **row,
                "precision": _ratio(row["tp"], row["tp"] + row["fp"]),
                "recall": _ratio(row["tp"], row["tp"] + row["fn"]),
            }
        )
    precision = {
        language: _ratio(total["tp"], total["tp"] + total["fp"])
        for language, total in sorted(language_totals.items())
    }
    recall = _ratio(tp_all, tp_all + fn_all)
    failures = [
        f"precision[{language}]={value} < {thresholds['precision'][language]}"
        for language, value in precision.items()
        if value < float(thresholds["precision"][language])
    ]
    if recall < float(thresholds["recall_global"]):
        failures.append(f"recall={recall} < {thresholds['recall_global']}")
    if bounded_fp > int(thresholds["bounded_false_positives"]):
        failures.append(f"bounded_false_positives={bounded_fp}")
    for entry in rows:
        label = f"{entry['rule']}/{entry['language']}"
        if float(str(entry["recall"])) < float(thresholds["recall_global"]):
            failures.append(f"recall[{label}]={entry['recall']}")
        if float(str(entry["precision"])) < float(thresholds["precision"][entry["language"]]):
            failures.append(f"precision[{label}]={entry['precision']}")
    failures.extend(f"coverage {gap}" for gap in coverage_gaps)
    return {
        "passed": not failures,
        "cases": len(cases),
        "precision": precision,
        "recall_global": recall,
        "bounded_false_positives": bounded_fp,
        "failures": failures,
        "mismatches": mismatches,
        "rows": rows,
    }
