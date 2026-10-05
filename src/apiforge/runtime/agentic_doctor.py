"""`doctor --agentic`: cross-plane agentic health, read-only and local.

Each section reads persisted state only (case, memory store, trust
policies, telemetry spans, eval corpora, SDD chain, MCP registry and the
economy doctor). Missing inputs resolve to ``unresolved`` — an absent
artifact is a named gap, never an implied failure or an implied pass.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml

from apiforge.contracts.agentic_health import (
    AgenticDoctorReport,
    AgenticDoctorSection,
    PlaneState,
)
from apiforge.contracts.economy_extras import DoctorFinding

_RULES = Path("src/apiforge/rules")


def _finding(code: str, severity: str, detail: str, unlock: str) -> DoctorFinding:
    return DoctorFinding(code=code, severity=severity, detail=detail, unlock=unlock)  # type: ignore[arg-type]


def _jsonl_count(path: Path) -> int | None:
    if not path.is_file():
        return None
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            count += 1
    return count


def _case_section(root: Path) -> AgenticDoctorSection:
    case = root / ".apiforge" / "case" / "case.json"
    if not case.is_file():
        return AgenticDoctorSection(
            plane="case",
            state="unresolved",
            checks=("case-persistence",),
            unresolved=(
                "no persisted case under .apiforge/case/ — create or load one before governed work",
            ),
        )
    try:
        json.loads(case.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return AgenticDoctorSection(
            plane="case",
            state="attention",
            checks=("case-persistence",),
            findings=(
                _finding(
                    "AF-DOCTOR-CASE-INVALID",
                    "warning",
                    f"persisted case fails to parse: {exc}",
                    "repair or regenerate the case via `apiforge analyze`",
                ),
            ),
        )
    return AgenticDoctorSection(plane="case", checks=("case-persistence",))


def _memory_section(root: Path) -> AgenticDoctorSection:
    from apiforge.memory.store import list_quarantine

    memory_dir = root / ".apiforge" / "memory"
    if not memory_dir.is_dir():
        return AgenticDoctorSection(
            plane="memory",
            state="unresolved",
            checks=("memory-store", "quarantine-backlog"),
            unresolved=("no .apiforge/memory store yet — first governed write creates it",),
        )
    backlog = list_quarantine(root)
    findings: tuple[DoctorFinding, ...] = ()
    state: PlaneState = "ok"
    if backlog:
        state = "attention"
        findings = (
            _finding(
                "AF-DOCTOR-MEMORY-QUARANTINE",
                "warning",
                f"{len(backlog)} memory candidate(s) quarantined awaiting human resolution",
                "review via `apiforge memory quarantine` and resolve each row",
            ),
        )
    return AgenticDoctorSection(
        plane="memory",
        state=state,
        checks=("memory-store", "quarantine-backlog"),
        findings=findings,
    )


def _trust_section(root: Path) -> AgenticDoctorSection:
    checks = ("tool-risk-policy", "trust-policy-parse")
    findings: list[DoctorFinding] = []
    policy = root / _RULES / "tool_risk.yaml"
    if not policy.is_file():
        findings.append(
            _finding(
                "AF-DOCTOR-TRUST-POLICY-MISSING",
                "warning",
                "rules/tool_risk.yaml is missing — tool authorization cannot be allowlist-first",
                "restore the declared tool-risk policy",
            )
        )
        return AgenticDoctorSection(
            plane="trust", state="attention", checks=checks, findings=tuple(findings)
        )
    try:
        from apiforge.trust.tools import load_tool_risk

        load_tool_risk(policy)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        # policy parse failures surface as findings; they never crash the doctor
        findings.append(
            _finding(
                "AF-DOCTOR-TRUST-POLICY-INVALID",
                "warning",
                f"tool-risk policy fails to load: {exc}",
                "repair rules/tool_risk.yaml",
            )
        )
        return AgenticDoctorSection(
            plane="trust", state="attention", checks=checks, findings=tuple(findings)
        )
    return AgenticDoctorSection(plane="trust", checks=checks)


def _telemetry_section(root: Path) -> AgenticDoctorSection:
    spans = _jsonl_count(root / ".apiforge" / "telemetry" / "agent-spans.jsonl")
    if spans is None:
        return AgenticDoctorSection(
            plane="telemetry",
            state="unresolved",
            checks=("span-store",),
            unresolved=("no agent-spans.jsonl yet — spans appear after governed runs",),
        )
    return AgenticDoctorSection(plane="telemetry", checks=("span-store", f"spans-observed:{spans}"))


def _evals_section(root: Path) -> AgenticDoctorSection:
    corpus_root = root / "evals" / "corpus"
    if not corpus_root.is_dir():
        return AgenticDoctorSection(
            plane="evals",
            state="unresolved",
            checks=("corpus-presence", "corpus-parse"),
            unresolved=("evals/corpus is absent — the deterministic eval wave has no corpora",),
        )
    findings: list[DoctorFinding] = []
    corpora = 0
    for directory in sorted(p for p in corpus_root.iterdir() if p.is_dir()):
        if not (directory / "README.md").is_file():
            findings.append(
                _finding(
                    "AF-DOCTOR-EVAL-CORPUS-README",
                    "info",
                    f"{directory.name}: corpus directory lacks a README",
                    "add a README naming the corpus contract",
                )
            )
        for yaml_path in sorted(directory.glob("*.yaml")):
            try:
                yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                findings.append(
                    _finding(
                        "AF-DOCTOR-EVAL-CORPUS-PARSE",
                        "warning",
                        f"{directory.name}/{yaml_path.name}: {exc}",
                        "repair the corpus yaml",
                    )
                )
        corpora += 1
    state: PlaneState = "attention" if any(f.severity == "warning" for f in findings) else "ok"
    return AgenticDoctorSection(
        plane="evals",
        state=state,
        checks=("corpus-presence", "corpus-parse", f"corpora-observed:{corpora}"),
        findings=tuple(findings),
    )


def _sdd_section(root: Path) -> AgenticDoctorSection:
    sdd_root = root / "docs" / "sdd"
    if not sdd_root.is_dir():
        return AgenticDoctorSection(
            plane="sdd",
            state="unresolved",
            checks=("sdd-root",),
            unresolved=("docs/sdd absent — no SDD features tracked",),
        )
    features = [d for d in sorted(sdd_root.iterdir()) if d.is_dir()]
    findings: list[DoctorFinding] = []
    for feature in features:
        for phase in ("discover.md", "ship.md"):
            if not (feature / phase).is_file():
                findings.append(
                    _finding(
                        "AF-DOCTOR-SDD-CHAIN-GAP",
                        "warning",
                        f"{feature.name}: missing {phase} — hash chain incomplete",
                        "complete the SDD phase chain and restamp upstreams",
                    )
                )
    return AgenticDoctorSection(
        plane="sdd",
        state="attention" if findings else "ok",
        checks=("sdd-root", f"features-observed:{len(features)}"),
        findings=tuple(findings),
    )


def _mcp_section() -> AgenticDoctorSection:
    from apiforge.mcp.tools import TOOLS

    return AgenticDoctorSection(
        plane="mcp", checks=("tool-registry", f"tools-declared:{len(TOOLS)}")
    )


def _economy_section(root: Path) -> AgenticDoctorSection:
    from apiforge.economy.doctor import diagnose

    report = diagnose(root)
    return AgenticDoctorSection(
        plane="economy",
        state="attention" if report.findings else "ok",
        checks=report.checks,
        findings=report.findings,
    )


def diagnose_agentic(root: Path) -> AgenticDoctorReport:
    """Aggregate health across every declared plane. Never mutates."""
    sections = (
        _case_section(root),
        _memory_section(root),
        _trust_section(root),
        _telemetry_section(root),
        _evals_section(root),
        _sdd_section(root),
        _mcp_section(),
        _economy_section(root),
    )
    findings = tuple(f for section in sections for f in section.findings)
    unresolved = tuple(u for section in sections for u in section.unresolved)
    status: Literal["ok", "attention", "unresolved"]
    if all(section.state == "unresolved" for section in sections):
        status = "unresolved"
    elif findings:
        status = "attention"
    else:
        status = "ok"
    return AgenticDoctorReport(
        sections=sections, findings=findings, unresolved=unresolved, status=status
    )
