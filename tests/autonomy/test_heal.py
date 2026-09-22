"""Self-healing pipeline — 8 stages, policy-decided, rollback operational."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.autonomy.heal import STAGES, HealError, run_heal
from apiforge.autonomy.modes import parse_mode
from apiforge.autonomy.service import read_ledger, set_mode
from apiforge.dispatch.runner import DispatchContext
from apiforge.policy.loader import DEFAULT_POLICY


def _ctx(root: Path, **kw: object) -> DispatchContext:
    return DispatchContext(case=root / ".apiforge", **kw)  # type: ignore[arg-type]


def _set(root: Path, mode: str, **detail: str) -> None:
    set_mode(
        root,
        parse_mode(mode),
        actor="tester",
        now="2026-01-01T00:00:00Z",
        reason="test",
        policy=DEFAULT_POLICY,
        detail=detail,
    )


def _findings_file(root: Path, findings: list[dict[str, object]]) -> Path:
    path = root / "findings.json"
    path.write_text(json.dumps({"findings": findings}), encoding="utf-8")
    return path


_CONFIRMED = {
    "finding_id": "F-1",
    "rule_id": "AF-PERF-101",
    "status": "confirmed",
    "severity": "high",
    "title": "HTTP call without timeout",
    "evidence": ["fact-1"],
}


def test_observe_records_every_stage(tmp_path: Path) -> None:
    result = run_heal(
        tmp_path,
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
        detail={},
    )
    assert result["resolution"] == "observed"
    names = [s["stage"] for s in result["stages"]]
    assert names[:-1] == list(STAGES[:-1])
    assert names[-1] in ("accept", "rollback")
    assert all(s["outcome"] == "observed" for s in result["stages"])
    entries = [e for e in read_ledger(tmp_path) if e["event"] == "heal.stage"]
    assert len(entries) == 8


def test_detect_no_signal_accepts(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    findings = _findings_file(
        tmp_path,
        [
            {
                "finding_id": "F-u",
                "rule_id": "AF-PERF-101",
                "status": "unresolved",
                "severity": "low",
                "title": "t",
                "evidence": [],
            }
        ],
    )
    result = run_heal(
        tmp_path,
        ctx=_ctx(tmp_path, findings=findings),
        policy=DEFAULT_POLICY,
        detail={},
    )
    assert result["resolution"] == "accepted"
    assert result["reason"] == "no_signal"


def test_detect_requires_findings(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    with pytest.raises(HealError, match="AF-HEAL-NO-FINDINGS"):
        run_heal(
            tmp_path,
            ctx=_ctx(tmp_path),
            policy=DEFAULT_POLICY,
            detail={},
        )


def test_authorize_gate_halts_and_names_missing(tmp_path: Path) -> None:
    """AT-005: destructive class without approval — nothing executes."""
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    findings = _findings_file(tmp_path, [_CONFIRMED])
    result = run_heal(
        tmp_path,
        ctx=_ctx(tmp_path, findings=findings),
        policy=DEFAULT_POLICY,
        detail={},
        action_class="destructive",
    )
    assert result["resolution"] == "pending"
    authorize = next(s for s in result["stages"] if s["stage"] == "authorize")
    assert authorize["outcome"] == "gate"
    assert "confirmation" in authorize["missing"]
    assert not any(s["stage"] == "execute" and s["outcome"] == "ok" for s in result["stages"])


def test_local_reversible_executes_then_rolls_back(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    findings = _findings_file(tmp_path, [_CONFIRMED])
    target = tmp_path / "app.py"
    target.write_text("x = 1\n", encoding="utf-8")
    before = target.read_bytes()
    result = run_heal(
        tmp_path,
        ctx=_ctx(tmp_path, findings=findings),
        policy=DEFAULT_POLICY,
        detail={},
        action_class="local_reversible",
        writable_paths=(str(target),),
    )
    # remediate steps are not dispatchable — verify finds no change, the
    # rollback stage restores the snapshot and re-hashes the file.
    assert result["resolution"] == "rolled_back"
    resolve = next(s for s in result["stages"] if s["stage"] == "rollback")
    assert resolve["restored"][str(target)] == "restored"
    assert target.read_bytes() == before


def test_rollback_restores_bytes(tmp_path: Path) -> None:
    """An executed-looking mutation is reverted byte-for-byte."""
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    findings = _findings_file(tmp_path, [_CONFIRMED])
    target = tmp_path / "config.yaml"
    target.write_text("timeout: 0\n", encoding="utf-8")
    result = run_heal(
        tmp_path,
        ctx=_ctx(tmp_path, findings=findings),
        policy=DEFAULT_POLICY,
        detail={},
        writable_paths=(str(target),),
    )
    assert result["resolution"] == "rolled_back"
    assert target.read_text(encoding="utf-8") == "timeout: 0\n"


def test_ledger_records_resolution(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    findings = _findings_file(tmp_path, [_CONFIRMED])
    run_heal(
        tmp_path,
        ctx=_ctx(tmp_path, findings=findings),
        policy=DEFAULT_POLICY,
        detail={},
    )
    final = [e for e in read_ledger(tmp_path) if e["event"] == "heal"]
    assert final[-1]["resolution"] == "rolled_back"
