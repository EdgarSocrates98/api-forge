"""Autonomy modes — observe records, supervised gates, continuous continues."""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.autonomy.modes import (
    AutonomyError,
    AutonomyMode,
    load_mode,
    parse_mode,
)
from apiforge.autonomy.service import (
    RunbookError,
    read_ledger,
    run_action,
    run_runbook,
    set_mode,
)
from apiforge.dispatch.runner import DispatchContext
from apiforge.policy.loader import DEFAULT_POLICY, load_policy_from_text


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
        requested=mode,
    )


def test_default_mode_is_observe(tmp_path: Path) -> None:
    assert load_mode(tmp_path).mode is AutonomyMode.OBSERVE


def test_parse_mode_unknown_refuses() -> None:
    with pytest.raises(AutonomyError, match="AF-AUTONOMY-MODE-UNKNOWN"):
        parse_mode("yolo")


def test_observe_records_without_executing(tmp_path: Path) -> None:
    entry = run_action(
        tmp_path,
        "rules list",
        action_class="read_only",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
    )
    assert entry["outcome"] == "observed"
    assert entry["decision"] == "allow"


def test_escalation_is_gated_by_policy(tmp_path: Path) -> None:
    with pytest.raises(AutonomyError, match="AF-AUTONOMY-SET-REFUSED"):
        set_mode(
            tmp_path,
            AutonomyMode.SUPERVISED,
            actor="tester",
            now=None,
            reason="",
            policy=DEFAULT_POLICY,
            detail={},
        )
    # the refusal itself is recorded
    ledger = read_ledger(tmp_path)
    assert ledger[-1]["result"] == "refused"
    assert "approval" in ledger[-1]["missing"]


def test_escalation_with_approval_applies(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    assert load_mode(tmp_path).mode is AutonomyMode.SUPERVISED
    assert load_mode(tmp_path).set_by == "tester"


def test_deescalation_to_observe_always_allowed(tmp_path: Path) -> None:
    _set(tmp_path, "continuous", evidence="e1", approval="ops")
    _set(tmp_path, "observe")  # no gate detail needed — rule allows it
    assert load_mode(tmp_path).mode is AutonomyMode.OBSERVE


def test_supervised_executes_allow(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    entry = run_action(
        tmp_path,
        "rules list --area DATA",
        action_class="read_only",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
    )
    assert entry["outcome"] == "executed"
    assert entry["output_sha256"]


def test_supervised_gate_records_pending(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    entry = run_action(
        tmp_path,
        "model redis",
        action_class="sensitive",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
    )
    assert entry["outcome"] == "pending"
    assert "approval" in entry["missing"]


def test_deny_is_recorded_and_refused(tmp_path: Path) -> None:
    _set(tmp_path, "continuous", evidence="e1", approval="ops")
    policy = load_policy_from_text(
        "version: 1\n"
        "defaults: {read_only: allow, local_reversible: allow, sensitive: gate,"
        " external_mutation: gate, destructive: gate, irreversible: deny}\n"
        "rules:\n"
        "  - name: deny-redis\n    match: {verb: 'model redis'}\n    decision: deny\n"
    )
    entry = run_action(
        tmp_path,
        "model redis",
        action_class="read_only",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),
        policy=policy,
    )
    assert entry["outcome"] == "denied"
    assert entry["rule"] == "deny-redis"


def test_not_dispatchable_recorded(tmp_path: Path) -> None:
    _set(tmp_path, "continuous", evidence="e1", approval="ops")
    entry = run_action(
        tmp_path,
        "collect api-gateway",
        action_class="read_only",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
    )
    assert entry["outcome"] == "not_dispatchable"


def test_pending_input_is_pending_not_executed(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    entry = run_action(
        tmp_path,
        "model redis",
        action_class="read_only",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),  # no input_path
        policy=DEFAULT_POLICY,
    )
    assert entry["outcome"] == "pending"
    assert "input_path" in entry["missing_inputs"]


def test_runbook_observes_every_step(tmp_path: Path) -> None:
    result = run_runbook(
        tmp_path,
        "perf-watch",
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
        detail={},
    )
    assert result["mode"] == "observe"
    assert result["executed"] == 0
    assert all(s["outcome"] == "observed" for s in result["steps"])


def test_runbook_supervised_halts_on_pending(tmp_path: Path) -> None:
    _set(tmp_path, "supervised", evidence="e1", approval="ops")
    # perf-watch: model otel needs input_path (absent) -> pending -> halt
    result = run_runbook(
        tmp_path,
        "perf-watch",
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
        detail={},
    )
    assert result["halted"] is True
    assert result["steps"][0]["outcome"] == "pending"
    assert result["steps"][1]["outcome"] == "not_reached"


def test_runbook_continuous_continues_past_pending(tmp_path: Path) -> None:
    import json

    from apiforge.adapters.otel.extract import extract_otel
    from apiforge.adapters.otel.run import build_performance_run

    _set(tmp_path, "continuous", evidence="e1", approval="ops")
    fixture = Path("tests/fixtures/otel")
    base_run = tmp_path / "base-run.json"
    cand_run = tmp_path / "cand-run.json"
    for name, out in (("baseline.json", base_run), ("candidate.json", cand_run)):
        run = build_performance_run(extract_otel(fixture / name), name)
        out.write_text(json.dumps(run.model_dump(mode="json")), encoding="utf-8")
    result = run_runbook(
        tmp_path,
        "perf-watch",
        ctx=_ctx(
            tmp_path,
            input_path=fixture / "baseline.json",
            baseline=base_run,
            candidate=cand_run,
        ),
        policy=DEFAULT_POLICY,
        detail={},
    )
    assert result["halted"] is False
    assert [s["outcome"] for s in result["steps"]] == ["executed", "executed"]


def test_runbook_unknown_named(tmp_path: Path) -> None:
    with pytest.raises(RunbookError, match="AF-AUTONOMY-RUNBOOK-UNKNOWN"):
        run_runbook(tmp_path, "nope", ctx=_ctx(tmp_path), policy=DEFAULT_POLICY, detail={})


def test_ledger_is_append_only_and_recorded(tmp_path: Path) -> None:
    run_action(
        tmp_path,
        "rules list",
        action_class="read_only",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
    )
    run_action(
        tmp_path,
        "rules list",
        action_class="read_only",
        args=(),
        target=None,
        detail={},
        ctx=_ctx(tmp_path),
        policy=DEFAULT_POLICY,
    )
    entries = read_ledger(tmp_path)
    assert len(entries) == 2
    assert all(e["event"] == "action" for e in entries)


def test_v1_mode_names_resolve_through_map(tmp_path: Path) -> None:
    """AT-008: v1's five names resolve; the requested name is recorded."""
    from apiforge.autonomy.modes import V1_MODE_MAP

    assert parse_mode("recommend") is AutonomyMode.OBSERVE
    assert parse_mode("sandbox") is AutonomyMode.SUPERVISED
    assert parse_mode("approved") is AutonomyMode.SUPERVISED
    assert parse_mode("continuous") is AutonomyMode.CONTINUOUS
    assert set(V1_MODE_MAP) == {"observe", "recommend", "sandbox", "approved", "continuous"}
    _set(tmp_path, "sandbox", evidence="e1", approval="ops")
    assert load_mode(tmp_path).mode is AutonomyMode.SUPERVISED
    entry = read_ledger(tmp_path)[-1]
    assert entry["requested"] == "sandbox"
    assert entry["to"] == "supervised"
