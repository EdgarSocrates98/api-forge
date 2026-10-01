"""Deterministic gap report: Wilson 95% CI, theme qualification, H1 verdict, A/B deltas.

Only baseline runs whose current receipt says ``agree`` enter the counts;
disagreement, a missing verdict or a stale receipt keeps the run under
``unresolved_runs``. H1 and roadmap recommendations are decided only when the
cycle is ``ready``; otherwise the verdict is exposed as ``provisional_h1``.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime
from pathlib import Path

from apiforge.contracts.field import (
    EXIT_REASONS,
    SCENARIOS,
    AbDelta,
    CorpusManifest,
    FieldReport,
    FieldRun,
    H1Verdict,
    ThemeCount,
)
from apiforge.field.corpus import load_corpus
from apiforge.field.identity import ensure_cycle
from apiforge.field.readiness import cycle_state, verification_state
from apiforge.field.store import load_runs

Z95 = 1.959964


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4))


def _ab(runs: tuple[FieldRun, ...]) -> tuple[AbDelta, ...]:
    baseline = {run.task_id: run for run in runs if run.phase == "baseline"}
    deltas: list[AbDelta] = []
    for run in sorted((item for item in runs if item.phase == "ab_on"), key=lambda r: r.task_id):
        base = baseline.get(run.task_id)
        if base is None:
            continue
        before = base.time_to_solution_ms
        after = run.time_to_solution_ms
        deltas.append(
            AbDelta(
                task_id=run.task_id,
                baseline_manual_context=base.manual_context_required,
                ab_manual_context=run.manual_context_required,
                baseline_time_to_solution_ms=before,
                ab_time_to_solution_ms=after,
                time_delta_ms=after - before if before is not None and after is not None else None,
            )
        )
    return tuple(deltas)


def summarize(
    manifest: CorpusManifest,
    runs: tuple[FieldRun, ...],
    *,
    ab: bool = False,
    now: datetime | None = None,
) -> FieldReport:
    gate = manifest.gate
    baseline = tuple(run for run in runs if run.phase == "baseline")
    states = {run.task_id: verification_state(run) for run in baseline}
    verified = tuple(run for run in baseline if states[run.task_id] == "agree")
    judged = [run for run in baseline if states[run.task_id] in ("agree", "disagree")]
    disagree = sum(1 for run in judged if states[run.task_id] == "disagree")
    n = len(verified)

    by_reason: Counter[str] = Counter()
    repos_by_reason: dict[str, set[str]] = {}
    for run in verified:
        if run.exit_reason is None:
            continue
        by_reason[run.exit_reason] += 1
        repos_by_reason.setdefault(run.exit_reason, set()).add(run.repo_ref)

    themes: list[ThemeCount] = []
    for reason in EXIT_REASONS:
        count = by_reason.get(reason, 0)
        repos = len(repos_by_reason.get(reason, set()))
        themes.append(
            ThemeCount(
                exit_reason=reason,  # type: ignore[arg-type]
                count=count,
                repos=repos,
                share=round(count / n, 4) if n else 0.0,
                ci95=wilson(count, n),
                qualified=reason != "none"
                and count >= gate.min_tasks_per_theme
                and repos >= gate.min_repos_per_theme,
            )
        )
    qualified = sorted(
        (theme for theme in themes if theme.qualified), key=lambda t: (-t.count, t.exit_reason)
    )
    qualified_names = tuple(theme.exit_reason for theme in qualified)
    category = manifest.hypothesis.category
    top = qualified[0].count if qualified else 0
    h1_theme = next((theme for theme in qualified if theme.exit_reason == category), None)
    provisional: H1Verdict
    if h1_theme is not None and h1_theme.count == top:
        provisional = "confirmed"
    elif qualified:
        provisional = "refuted"
    else:
        provisional = "inconclusive"
    status, coverage = cycle_state(manifest, runs, now)

    scenario_counts: Counter[str] = Counter(str(run.scenario) for run in verified)
    under = tuple(
        scenario
        for scenario in SCENARIOS
        if scenario_counts.get(scenario, 0) < gate.min_tasks_per_scenario
    )
    verdict: H1Verdict = provisional if status == "ready" else "inconclusive"
    if status == "collecting":
        recommendation = "continue collecting: cycle not ready; open no new feature"
    elif status == "ready" and qualified_names:
        leaders = ", ".join(qualified_names[:2])
        recommendation = f"open follow-up SDDs for at most two themes: {leaders}"
    else:
        recommendation = "inconclusive: extend the corpus; open no new feature"

    return FieldReport(
        cycle_status=status,
        coverage_gate=coverage,
        runs_total=len(baseline),
        runs_verified=n,
        repos=len({run.repo_ref for run in verified}),
        scenario_counts=tuple(
            (scenario, scenario_counts.get(scenario, 0)) for scenario in SCENARIOS
        ),
        scenarios_under_min=under,
        themes=tuple(themes),
        qualified_themes=qualified_names,
        hypothesis=manifest.hypothesis,
        provisional_h1=provisional,
        h1_verdict=verdict,
        divergence_rate=round(disagree / len(judged), 4) if judged else 0.0,
        contaminated_runs=tuple(sorted(run.task_id for run in baseline if run.inference_flag)),
        unresolved_runs=tuple(
            sorted(run.task_id for run in baseline if states[run.task_id] != "agree")
        ),
        stale_runs=tuple(sorted(run.task_id for run in baseline if states[run.task_id] == "stale")),
        ab=_ab(runs) if ab else (),
        recommendation=recommendation,
    )


def build_report(root: Path, *, ab: bool = False, now: datetime | None = None) -> FieldReport:
    root = Path(root)
    manifest = load_corpus(root)
    ensure_cycle(root, manifest)
    return summarize(manifest, load_runs(root), ab=ab, now=now)


__all__ = ["Z95", "build_report", "summarize", "wilson"]
