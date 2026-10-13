"""`apiforge economy doctor` (§55): what in this setup makes runs pay more than needed.

Every check reads local state only (environment, manifests, policies, the
ledger, stored runs, pack metadata) and reports a finding with the unlock
that removes it. Nothing is changed.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, date, datetime
from pathlib import Path

from apiforge.contracts.economy_extras import DoctorFinding, EconomyDoctor

STALE_DAYS = 180
CHECKS = (
    "cache-enabled",
    "default-profile",
    "capsule-usage",
    "output-mode",
    "shared-cache",
    "knowledge-freshness",
    "token-receipts",
    "escalation-rate",
    "repeated-parsing",
)


def _finding(code: str, severity: str, detail: str, unlock: str) -> DoctorFinding:
    return DoctorFinding(code=code, severity=severity, detail=detail, unlock=unlock)  # type: ignore[arg-type]


def _ledger_rows(root: Path) -> list[dict[str, object]]:
    path = root / ".apiforge" / "economy.jsonl"
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def diagnose(root: Path, *, today: date | None = None) -> EconomyDoctor:
    from apiforge.cache.store import cache_enabled
    from apiforge.runtime.economy import load_economy_config, manifest_profile

    root = Path(root).resolve()
    moment = today or datetime.now(UTC).date()
    findings: list[DoctorFinding] = []
    if not cache_enabled():
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-CACHE-OFF",
                "warning",
                "APIFORGE_CACHE disables the graph/impact/capsule caches",
                "unset APIFORGE_CACHE or set it to on",
            )
        )
    configured = manifest_profile(root) or load_economy_config().get("default_profile")
    if configured == "deep":
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-DEEP-DEFAULT",
                "warning",
                "the default economy profile is deep; every run pays the widest envelope",
                "set economy_profile: balanced in .apiforge/project.yaml and pass --profile deep when needed",
            )
        )
    rows = _ledger_rows(root)
    verbs = [str(row.get("verb", "")) for row in rows]
    if any(
        "context resolve" in verb or verb.endswith("context_funnel") for verb in verbs
    ) and not any("capsule" in verb for verb in verbs):
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-NO-CAPSULE",
                "warning",
                "context is resolved at repository scope but no capsule was ever built",
                "use `apiforge context capsule --target '<METHOD> /path'` for operation questions",
            )
        )
    if os.environ.get("APIFORGE_OUTPUT", "json").lower() != "compact":
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-VERBOSE-OUTPUT",
                "info",
                "CLI payloads are pretty-printed json",
                "set APIFORGE_OUTPUT=compact for agent hosts",
            )
        )
    if not os.environ.get("APIFORGE_CACHE_HOME"):
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-NO-SHARED-CACHE",
                "info",
                "no shared cache tier; identical inputs in other roots are recomputed",
                "set APIFORGE_CACHE_HOME to a user or workspace directory",
            )
        )
    stale = _stale_packs(root, moment)
    if stale:
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-STALE-KNOWLEDGE",
                "warning",
                f"{len(stale)} pack(s) verified more than {STALE_DAYS} days ago: {', '.join(stale[:5])}",
                "refresh the packs with a read-only source receipt (`apiforge knowledge freshness`)",
            )
        )
    attributed = [row for row in rows if row.get("schema") == "apiforge/run-ledger-entry/v1"]
    observed = any(
        isinstance(row.get("cost"), dict) and row["cost"].get("observed_tokens")  # type: ignore[attr-defined]
        for row in attributed
    )
    if attributed and not observed:
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-TOKENS-UNRESOLVED",
                "info",
                "no run carries observed tokens; savings are measured in bytes only",
                "pass a host transcript to `apiforge economy stats --transcript`",
            )
        )
    rate = _escalation_rate(root)
    if rate is not None and rate > 0.5:
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-ESCALATION-HEAVY",
                "warning",
                f"{rate:.0%} of runs escalated to an L3 review",
                "inspect `apiforge economy roi`; raise specialist confidence or evidence before escalating",
            )
        )
    misses = sum(
        1
        for row in rows
        if str(row.get("verb", "")).startswith("cache:extract")
        and row.get("detail_level") == "miss"
    )
    hits = sum(
        1
        for row in rows
        if str(row.get("verb", "")).startswith("cache:extract") and row.get("detail_level") == "hit"
    )
    if misses > 3 and misses > hits:
        findings.append(
            _finding(
                "AF-ECONOMY-DOCTOR-REPEATED-PARSING",
                "warning",
                f"extractor cache missed {misses} times vs {hits} hits",
                "pass --cache-dir to analyze so unchanged trees reuse the extraction",
            )
        )
    warnings = any(item.severity == "warning" for item in findings)
    return EconomyDoctor(
        findings=tuple(findings), checks=CHECKS, status="attention" if warnings else "ok"
    )


def _stale_packs(root: Path, today: date) -> list[str]:
    from apiforge.knowledge.loader import load_packs
    from apiforge.knowledge.selector import default_root

    try:
        packs = load_packs(
            default_root(root / "knowledge" if (root / "knowledge").is_dir() else None)
        )
    except Exception:  # noqa: BLE001 - doctor never fails on a pack problem
        return []
    stale = []
    for name, pack in sorted(packs.items()):
        try:
            verified = date.fromisoformat(str(pack.verified))
        except ValueError:
            stale.append(name)
            continue
        if (today - verified).days > STALE_DAYS:
            stale.append(name)
    return stale


def _escalation_rate(root: Path) -> float | None:
    tasks = root / ".apiforge" / "tasks"
    if not tasks.is_dir():
        return None
    total = escalated = 0
    for summary in tasks.glob("*/runs/*/summary.json"):
        economy = json.loads(summary.read_text(encoding="utf-8")).get("economy") or {}
        if not economy:
            continue
        total += 1
        escalated += int(any(step.get("level") == "L3" for step in economy.get("ladder") or []))
    return escalated / total if total else None


__all__ = ["CHECKS", "diagnose"]
