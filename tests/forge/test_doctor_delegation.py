"""``forge doctor`` delegation lane (lf-0030, PHASE 7).

Discovery states, the frozen ``--format agent`` parser, governed argv-only
execution, exit-code classification, refusals persisted as records, the
before/after compare, and the read-only boundary — the lane collects
evidence, it never mutates.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.contracts.base import ContractError
from apiforge.contracts.delegation import (
    DelegationChain,
    DoctorDelegationRecord,
    DoctorDiscovery,
    DoctorFindingRow,
    DoctorScan,
    DoctorUnknownRow,
    record_integrity,
)
from apiforge.forge import store
from apiforge.forge.doctor import (
    DelegationError,
    admit_hop,
    compare_delegations,
    compare_scans,
    delegate_doctor_scan,
    discover_doctor,
    doctor_scan_argv,
    mint_chain,
    parse_agent_output,
    run_doctor_scan,
    scrub_env,
)

RUNNER = CliRunner()

AGENT_OUT = (
    "# schema_version=1.0 tool_version=0.2.5\n"
    "# knowledge_versions=api@1.4,deps@2.1\n"
    "OAS001|HIGH|MEDIUM|api/orders.yaml:12|missing response schema\n"
    "APISEC002|CRITICAL|HIGH|svc/orders|unauthenticated write route\n"
    "DEP007|LOW|LOW|-|\n"
    "UNKNOWN|payments|runtime version not declared\n"
)


def _fake_doctor(tmp_path: Path, body: str) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    script = tmp_path / "forge-doctor-api"
    script.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return script


def _script(
    exit_code: int = 0,
    payload: str = AGENT_OUT,
    *,
    stderr_secret_probe: bool = False,
) -> str:
    lines = [
        'if [ "$1" = "--version" ]; then echo "forge-doctor-api 0.2.5"; exit 0; fi',
        'if [ "$1" = "scan" ]; then',
    ]
    if stderr_secret_probe:
        lines.append('  echo "SECRET=$SECRET_MARKER" >&2')
    lines.append("  cat <<'EOF'")
    lines.append(payload.rstrip("\n"))
    lines.append("EOF")
    lines.append(f"  exit {exit_code}")
    lines.append("fi")
    lines.append("exit 2")
    return "\n".join(lines)


def _verified(script: Path) -> DoctorDiscovery:
    return DoctorDiscovery(
        state="verified",
        binary=str(script),
        argv_prefix=(str(script),),
        cli_version="0.2.5",
        package_version="0.2.5",
    )


def _scan(
    run_id: str, findings: list[dict[str, object]], unknowns: list[str] | None = None
) -> DoctorScan:
    return DoctorScan(
        run_id=run_id,
        target="/proj",
        argv=("/bin/fdapi", "scan", "/proj", "--format", "agent"),
        exit_code=0,
        stdout_sha256="0" * 64,
        findings=tuple(DoctorFindingRow.model_validate(f) for f in findings),
        unknowns=tuple(DoctorUnknownRow(subject=s, missing="m") for s in (unknowns or [])),
    )


# ---------------------------------------------------------------------------
# Discovery — measured states, never declared
# ---------------------------------------------------------------------------


def test_discover_absent() -> None:
    d = discover_doctor(which=lambda _: None, package_version=lambda: None)
    assert d.state == "absent"
    assert d.argv_prefix == ()


def test_discover_verified_binary() -> None:
    d = discover_doctor(
        which=lambda n: "/usr/bin/forge-doctor-api",
        package_version=lambda: "0.2.5",
        probe=lambda argv: "0.2.5",
    )
    assert d.state == "verified"
    assert d.argv_prefix == ("/usr/bin/forge-doctor-api",)
    assert d.cli_version == "0.2.5"


def test_discover_untrusted_when_version_unproven() -> None:
    d = discover_doctor(
        which=lambda n: "/usr/bin/forge-doctor-api",
        package_version=lambda: "0.2.5",
        probe=lambda argv: None,
    )
    assert d.state == "untrusted"
    assert d.binary == "/usr/bin/forge-doctor-api"


def test_discover_package_fallback_runs_module() -> None:
    import sys

    d = discover_doctor(
        which=lambda _: None,
        package_version=lambda: "0.2.5",
        probe=lambda argv: "0.2.5",
    )
    assert d.state == "verified"
    assert d.argv_prefix == (sys.executable, "-m", "forge_doctor_api")


def test_version_probe_parses_identity(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, 'echo "forge-doctor-api 0.2.5"')
    from apiforge.forge.doctor import _probe_cli_version

    assert _probe_cli_version((str(script),)) == "0.2.5"


def test_version_probe_rejects_foreign_binary(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, 'echo "totally-not-doctor 9.9"')
    from apiforge.forge.doctor import _probe_cli_version

    assert _probe_cli_version((str(script),)) is None


# ---------------------------------------------------------------------------
# Parser — frozen line schema, severity/confidence verbatim
# ---------------------------------------------------------------------------


def test_parse_agent_output_verbatim() -> None:
    meta, findings, unknowns = parse_agent_output(AGENT_OUT)
    assert meta["schema_version"] == "1.0"
    assert meta["tool_version"] == "0.2.5"
    assert meta["knowledge_versions"] == {"api": "1.4", "deps": "2.1"}
    assert len(findings) == 3
    first = findings[0]
    assert (first.check_id, first.severity, first.confidence) == ("OAS001", "HIGH", "MEDIUM")
    assert first.subject == "api/orders.yaml"
    assert first.line == 12
    second = findings[1]
    assert (second.severity, second.confidence) == ("CRITICAL", "HIGH")
    assert second.subject == "svc/orders"
    assert second.line is None
    assert findings[2].subject == "-"
    assert unknowns[0].subject == "payments"
    assert unknowns[0].missing == "runtime version not declared"


def test_parse_missing_header_refused() -> None:
    with pytest.raises(DelegationError, match="AF-DELEG-INVALID-OUTPUT"):
        parse_agent_output("OAS001|HIGH|MEDIUM|s|desc\n")


def test_parse_bad_schema_major_refused() -> None:
    bad = "# schema_version=2.0 tool_version=0.3.0\nA|HIGH|LOW|s|d\n"
    with pytest.raises(DelegationError, match="AF-DELEG-INCOMPATIBLE"):
        parse_agent_output(bad)


def test_parse_malformed_rows_refused() -> None:
    for line in ("BROKEN|HIGH|MEDIUM", "|HIGH|MEDIUM|s|d", "UNKNOWN|"):
        bad = f"# schema_version=1.0 tool_version=0.2.5\n{line}\n"
        with pytest.raises(DelegationError, match="AF-DELEG-INVALID-OUTPUT"):
            parse_agent_output(bad)


def test_parse_description_keeps_pipes() -> None:
    out = "# schema_version=1.0 tool_version=0.2.5\nA|LOW|LOW|s|a|b|c\n"
    _, findings, _ = parse_agent_output(out)
    assert findings[0].description == "a|b|c"


# ---------------------------------------------------------------------------
# Closed argv template + env scrub
# ---------------------------------------------------------------------------


def test_argv_template_closed() -> None:
    argv = doctor_scan_argv(("/bin/fdapi",), "/proj")
    assert argv == ["/bin/fdapi", "scan", "/proj", "--format", "agent"]
    argv = doctor_scan_argv(("/bin/fdapi",), "/proj", fail_on=("security", "breaking"))
    assert argv[-2:] == ["--fail-on", "breaking,security"]


def test_fail_on_unknown_category_refused() -> None:
    with pytest.raises(DelegationError, match="AF-DELEG-INVALID-INPUT"):
        doctor_scan_argv(("/bin/fdapi",), "/proj", fail_on=("rm-rf",))


def test_read_only_guard_refuses_mutation() -> None:
    from apiforge.forge.doctor import _assert_read_only

    for argv in (
        ("fdapi", "safefix", "/proj"),
        ("fdapi", "scan", "/proj", "--format", "agent", "--out", "r.json"),
        ("fdapi", "scan", "/proj", "--format", "agent", "--incremental"),
        ("fdapi", "migrate", "/proj"),
    ):
        with pytest.raises(DelegationError, match="AF-DELEG-READ-ONLY"):
            _assert_read_only(argv, argv_prefix=("fdapi",), target="/proj")


def test_env_scrub_drops_credentials() -> None:
    env = scrub_env(
        {
            "PATH": "/usr/bin",
            "HOME": "/home/x",
            "AWS_SECRET_ACCESS_KEY": "k",
            "GITHUB_TOKEN": "t",
            "HTTP_PROXY": "http://user:pw@proxy",
            "CUSTOM_FLAG": "v",
        }
    )
    assert env["PATH"] == "/usr/bin"
    assert env["HOME"] == "/home/x"
    assert env["PYTHONUTF8"] == "1"
    for leaked in ("AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "HTTP_PROXY", "CUSTOM_FLAG"):
        assert leaked not in env


# ---------------------------------------------------------------------------
# Governed run — exit-code classification
# ---------------------------------------------------------------------------


def test_run_scan_parses_exit_zero(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(0))
    scan = run_doctor_scan(tmp_path, argv_prefix=(str(script),), run_id="drun-x")
    assert scan.exit_code == 0
    assert not scan.gate_failed
    assert len(scan.findings) == 3
    assert scan.tool_version == "0.2.5"


def test_run_scan_exit1_gate_tripped(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(1))
    scan = run_doctor_scan(tmp_path, argv_prefix=(str(script),))
    assert scan.exit_code == 1
    assert scan.gate_failed
    assert len(scan.findings) == 3  # the report is identical — findings still evidence


def test_run_scan_exit2_usage_refused(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, "exit 2")
    with pytest.raises(DelegationError, match="AF-DELEG-USAGE"):
        run_doctor_scan(tmp_path, argv_prefix=(str(script),))


def test_run_scan_other_exit_failed(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(9))
    with pytest.raises(DelegationError, match="AF-DELEG-FAILED"):
        run_doctor_scan(tmp_path, argv_prefix=(str(script),))


def test_run_scan_timeout(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, 'if [ "$1" = "scan" ]; then sleep 5; fi\nexit 0')
    with pytest.raises(DelegationError, match="AF-DELEG-TIMEOUT"):
        run_doctor_scan(tmp_path, argv_prefix=(str(script),), timeout=1)


def test_run_scan_output_cap_refused(tmp_path: Path) -> None:
    """A stdout flood is refused AF-DELEG-OUTPUT-LIMIT — never truncated."""
    body = 'if [ "$1" = "scan" ]; then head -c 9000000 /dev/zero | tr "\\0" "x"; fi\nexit 0'
    script = _fake_doctor(tmp_path, body)
    with pytest.raises(DelegationError, match="AF-DELEG-OUTPUT-LIMIT"):
        run_doctor_scan(tmp_path, argv_prefix=(str(script),))


def test_run_scan_credentials_never_reach_doctor(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(0, stderr_secret_probe=True))
    scan = run_doctor_scan(
        tmp_path,
        argv_prefix=(str(script),),
        env={"PATH": os.environ.get("PATH", ""), "SECRET_MARKER": "pwned"},
    )
    assert "SECRET=pwned" not in scan.stderr_tail
    assert "SECRET=" in scan.stderr_tail


# ---------------------------------------------------------------------------
# delegate_doctor_scan — the PHASE 7 evidence step
# ---------------------------------------------------------------------------


def test_delegate_persists_completed_record(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(0))
    target = tmp_path / "proj"
    target.mkdir()
    record = delegate_doctor_scan(
        tmp_path, target, correlation_id="corr-1", discovery=_verified(script)
    )
    assert record.status == "partial"  # UNKNOWN row present
    assert record.correlation_id == "corr-1"
    assert record.idempotency_key.startswith("idem-")
    assert record.source_provider == "forge-doctor-api"
    assert record.source_version == "0.2.5"
    assert record.integrity == record_integrity(record.model_copy(update={"integrity": None}))
    assert record.chain.visited_providers == ("api-forge", "forge-doctor-api")
    assert record.chain.delegation_depth == 1
    findings = {f.check_id: f for f in record.findings}
    assert findings["APISEC002"].severity == "CRITICAL"
    assert findings["APISEC002"].confidence == "HIGH"  # verbatim, never normalized
    directory = store.delegation_dir(tmp_path, record.run_id)
    assert (directory / "record.json").is_file()
    assert (directory / "scan.json").is_file()
    assert (directory / "scan.agent.txt").is_file()
    persisted = store.load_delegation(tmp_path, record.run_id)
    assert persisted.integrity == record.integrity


def test_delegate_absent_persists_refusal(tmp_path: Path) -> None:
    """Caso E: specialist absent → named refusal + a persisted refused record."""
    target = tmp_path / "proj"
    target.mkdir()
    absent = DoctorDiscovery(state="absent", detail="nothing found")
    with pytest.raises(DelegationError, match="AF-DELEG-ABSENT"):
        delegate_doctor_scan(tmp_path, target, discovery=absent)
    records = [store.load_delegation(tmp_path, run_id) for run_id in store.delegation_ids(tmp_path)]
    assert len(records) == 1
    assert records[0].status == "refused"
    assert records[0].error is not None
    assert records[0].error.code == "provider-absent"


def test_delegate_unverified_refused(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(0))
    target = tmp_path / "proj"
    target.mkdir()
    untrusted = DoctorDiscovery(
        state="untrusted", argv_prefix=(str(script),), detail="version unproven"
    )
    with pytest.raises(DelegationError, match="AF-DELEG-INCOMPATIBLE"):
        delegate_doctor_scan(tmp_path, target, discovery=untrusted)


def test_delegate_unverified_opt_in_records_limitation(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(0))
    target = tmp_path / "proj"
    target.mkdir()
    untrusted = DoctorDiscovery(
        state="untrusted", argv_prefix=(str(script),), detail="version unproven"
    )
    record = delegate_doctor_scan(tmp_path, target, discovery=untrusted, allow_unverified=True)
    assert record.status in ("completed", "partial")
    assert any("unverified" in lim for lim in record.limitations)


def test_delegate_bad_target_refused(tmp_path: Path) -> None:
    with pytest.raises(DelegationError, match="AF-DELEG-TARGET"):
        delegate_doctor_scan(tmp_path, tmp_path / "nope")


def test_delegate_policy_deny_refused(tmp_path: Path) -> None:
    from apiforge.policy.loader import load_policy_from_text

    policy = load_policy_from_text(
        "version: 1\n"
        "defaults:\n"
        "  read_only: deny\n"
        "  local_reversible: deny\n"
        "  sensitive: deny\n"
        "  external_mutation: deny\n"
        "  destructive: deny\n"
        "  irreversible: deny\n"
    )
    target = tmp_path / "proj"
    target.mkdir()
    with pytest.raises(DelegationError, match="AF-DELEG-POLICY"):
        delegate_doctor_scan(tmp_path, target, policy=policy)
    records = [store.load_delegation(tmp_path, r) for r in store.delegation_ids(tmp_path)]
    assert records[0].status == "refused"
    assert records[0].error is not None
    assert records[0].error.code == "policy-refusal"


def test_delegate_cycle_refused(tmp_path: Path) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    chain = DelegationChain(
        correlation_id="corr-c",
        delegation_depth=1,
        visited_providers=("api-forge", "forge-doctor-api"),
    )
    with pytest.raises(DelegationError, match="AF-DELEG-CYCLE"):
        delegate_doctor_scan(tmp_path, target, chain=chain)


def test_delegate_budget_exhausted_refused(tmp_path: Path) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    chain = DelegationChain(
        correlation_id="corr-b",
        delegation_depth=4,
        visited_providers=("a-forge", "b-forge", "c-forge", "d-forge", "e-forge"),
        max_hops=4,
    )
    with pytest.raises(DelegationError, match="AF-DELEG-BUDGET"):
        delegate_doctor_scan(tmp_path, target, chain=chain)


def test_delegate_failed_run_persists_failed(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(9))
    target = tmp_path / "proj"
    target.mkdir()
    with pytest.raises(DelegationError, match="AF-DELEG-FAILED"):
        delegate_doctor_scan(tmp_path, target, discovery=_verified(script))
    records = [store.load_delegation(tmp_path, r) for r in store.delegation_ids(tmp_path)]
    assert records[0].status == "failed"
    assert records[0].error is not None
    assert records[0].error.code == "runtime-error"


def test_delegate_invalid_output_persists_failed(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, _script(0, payload="garbage line"))
    target = tmp_path / "proj"
    target.mkdir()
    with pytest.raises(DelegationError, match="AF-DELEG-INVALID-OUTPUT"):
        delegate_doctor_scan(tmp_path, target, discovery=_verified(script))
    records = [store.load_delegation(tmp_path, r) for r in store.delegation_ids(tmp_path)]
    assert records[0].status == "failed"
    assert records[0].error is not None
    assert records[0].error.code == "invalid-output"


def test_delegate_timeout_persists_retryable_failure(tmp_path: Path) -> None:
    script = _fake_doctor(tmp_path, 'if [ "$1" = "scan" ]; then sleep 5; fi\nexit 0')
    target = tmp_path / "proj"
    target.mkdir()
    with pytest.raises(DelegationError, match="AF-DELEG-TIMEOUT"):
        delegate_doctor_scan(tmp_path, target, discovery=_verified(script), timeout=1)
    records = [store.load_delegation(tmp_path, r) for r in store.delegation_ids(tmp_path)]
    assert records[0].status == "failed"
    assert records[0].error is not None
    assert records[0].error.code == "timeout"
    assert records[0].error.retryable is True


# ---------------------------------------------------------------------------
# Chain semantics — mint + admit
# ---------------------------------------------------------------------------


def test_mint_chain_consumer_is_first_visited() -> None:
    chain = mint_chain(correlation_id="corr-9")
    assert chain.visited_providers == ("api-forge",)
    assert chain.delegation_depth == 0


def test_admit_hop_advances_and_decrements() -> None:
    chain = admit_hop(
        mint_chain(correlation_id="c", timeout_budget_s=600), "forge-doctor-api", cost_s=300
    )
    assert chain.visited_providers == ("api-forge", "forge-doctor-api")
    assert chain.delegation_depth == 1
    assert chain.timeout_budget_s == 300


def test_admit_hop_refuses_revisit() -> None:
    chain = mint_chain(correlation_id="c")
    with pytest.raises(DelegationError, match="AF-DELEG-CYCLE"):
        admit_hop(chain, "api-forge")


def test_admit_hop_refuses_exhausted_budget() -> None:
    chain = mint_chain(correlation_id="c", timeout_budget_s=60)
    with pytest.raises(DelegationError, match="AF-DELEG-BUDGET"):
        admit_hop(chain, "forge-doctor-api", cost_s=300)


# ---------------------------------------------------------------------------
# Before/after compare — the revalidation loop
# ---------------------------------------------------------------------------


def _row(
    check_id: str,
    severity: str = "HIGH",
    confidence: str = "MEDIUM",
    subject: str = "s",
    description: str = "d",
) -> dict[str, object]:
    return {
        "check_id": check_id,
        "severity": severity,
        "confidence": confidence,
        "subject": subject,
        "description": description,
    }


def test_compare_scans_names_added_removed_changed() -> None:
    baseline = _scan(
        "drun-a",
        [
            _row("OAS001", subject="api.yaml"),
            _row("OAS002", subject="gone.yaml"),
            _row("OAS003", severity="LOW", subject="sev.yaml"),
        ],
        unknowns=["u1"],
    )
    current = _scan(
        "drun-b",
        [
            _row("OAS001", subject="api.yaml"),
            _row("OAS003", severity="CRITICAL", subject="sev.yaml"),
            _row("OAS004", subject="new.yaml"),
        ],
        unknowns=["u2"],
    )
    delta = compare_scans(baseline, current)
    assert delta.delta_source == "apiforge-derived"
    assert delta.findings_added == ("OAS004|new.yaml",)
    assert delta.findings_removed == ("OAS002|gone.yaml",)
    assert delta.findings_changed == ("OAS003|sev.yaml",)
    assert delta.severity_changes == ("OAS003|sev.yaml: LOW->CRITICAL",)
    assert delta.unknowns_added == ("u2|m",)
    assert delta.unknowns_removed == ("u1|m",)
    assert not delta.empty


def test_compare_identical_scans_is_empty() -> None:
    rows = [_row("OAS001")]
    delta = compare_scans(_scan("drun-a", rows), _scan("drun-b", rows))
    assert delta.empty
    assert delta.findings_added == delta.findings_removed == delta.findings_changed == ()


def test_compare_delegations_persists_artifact(tmp_path: Path) -> None:
    for run_id, rows in (
        ("drun-before", [_row("A"), _row("B")]),
        ("drun-after", [_row("A"), _row("C")]),
    ):
        directory = store.delegation_dir(tmp_path, run_id)
        directory.mkdir(parents=True)
        (directory / "scan.json").write_text(
            _scan(run_id, rows).model_dump_json(indent=2), encoding="utf-8"
        )
    delta = compare_delegations(tmp_path, "drun-before", "drun-after")
    assert delta.baseline_ref == "drun-before"
    assert delta.findings_added == ("C|s",)
    assert delta.findings_removed == ("B|s",)
    artifact = store.delegation_dir(tmp_path, "drun-after") / "compare-drun-before.json"
    assert json.loads(artifact.read_text())["baseline_ref"] == "drun-before"


def test_compare_delegations_missing_run_named(tmp_path: Path) -> None:
    with pytest.raises(DelegationError, match="AF-DELEG-NOT-FOUND"):
        compare_delegations(tmp_path, "drun-none", "drun-also-none")


def test_full_revalidation_loop(tmp_path: Path) -> None:
    """Scan → (host change) → re-scan → compare — the PHASE 7 loop end to end."""
    target = tmp_path / "proj"
    target.mkdir()
    before = _fake_doctor(tmp_path / "before", _script(0, payload=AGENT_OUT))
    record_a = delegate_doctor_scan(tmp_path, target, discovery=_verified(before))
    after_payload = AGENT_OUT.replace("OAS001|HIGH|MEDIUM", "OAS001|HIGH|MEDIUM")
    after = _fake_doctor(
        tmp_path / "after",
        _script(0, payload=after_payload.replace("APISEC002|CRITICAL|HIGH", "APISEC002|LOW|LOW")),
    )
    record_b = delegate_doctor_scan(tmp_path, target, discovery=_verified(after))
    delta = compare_delegations(tmp_path, record_a.run_id, record_b.run_id)
    assert delta.baseline_ref == record_a.run_id
    assert delta.findings_changed == ("APISEC002|svc/orders",)
    assert delta.severity_changes == ("APISEC002|svc/orders: CRITICAL->LOW",)
    assert delta.confidence_changes == ("APISEC002|svc/orders: HIGH->LOW",)


# ---------------------------------------------------------------------------
# Contract + store invariants
# ---------------------------------------------------------------------------


def test_refused_record_requires_error() -> None:
    with pytest.raises(ValueError, match="requires an error"):
        DoctorDelegationRecord(
            run_id="drun-x",
            correlation_id="corr-x",
            idempotency_key="idem-x",
            status="refused",
        )


def test_completed_record_must_not_carry_error() -> None:
    from apiforge.contracts.delegation import DelegationErrorRecord

    with pytest.raises(ValueError, match="must not carry"):
        DoctorDelegationRecord(
            run_id="drun-x",
            correlation_id="corr-x",
            idempotency_key="idem-x",
            status="completed",
            error=DelegationErrorRecord(code="runtime-error"),
        )


def test_chain_rejects_revisit_encoding() -> None:
    with pytest.raises(ValueError, match="unique"):
        DelegationChain(visited_providers=("api-forge", "api-forge"), delegation_depth=1)


def test_store_refuses_duplicate_run(tmp_path: Path) -> None:
    from apiforge.contracts.delegation import DelegationErrorRecord

    record = DoctorDelegationRecord(
        run_id="drun-dup",
        correlation_id="corr-x",
        idempotency_key="idem-x",
        status="refused",
        error=DelegationErrorRecord(code="provider-absent"),
    )
    store.write_delegation(tmp_path, record)
    with pytest.raises(ContractError, match="AF-DELEG-EXISTS"):
        store.write_delegation(tmp_path, record)


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------


def test_cli_discover_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apiforge.forge.doctor.discover_doctor",
        lambda: DoctorDiscovery(state="absent", detail="nothing found"),
    )
    result = RUNNER.invoke(app, ["forge", "doctor", "discover"])
    assert result.exit_code == 0, result.output
    assert '"absent"' in result.output


def test_cli_scan_absent_named_refusal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apiforge.forge.doctor.discover_doctor",
        lambda: DoctorDiscovery(state="absent", detail="nothing found"),
    )
    target = tmp_path / "proj"
    target.mkdir()
    result = RUNNER.invoke(
        app, ["forge", "doctor", "scan", "--target", str(target), "--root", str(tmp_path)]
    )
    assert result.exit_code == 2
    assert "AF-DELEG-ABSENT" in result.output
    assert store.delegation_ids(tmp_path)


def test_cli_scan_and_compare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = _fake_doctor(tmp_path, _script(0))
    monkeypatch.setattr("apiforge.forge.doctor.discover_doctor", lambda: _verified(script))
    target = tmp_path / "proj"
    target.mkdir()
    result = RUNNER.invoke(
        app, ["forge", "doctor", "scan", "--target", str(target), "--root", str(tmp_path)]
    )
    assert result.exit_code == 0, result.output
    run_id = store.delegation_ids(tmp_path)[0]
    shown = RUNNER.invoke(
        app, ["forge", "doctor", "show", "--run", run_id, "--root", str(tmp_path)]
    )
    assert shown.exit_code == 0
    assert "OAS001" in shown.output
    listed = RUNNER.invoke(app, ["forge", "doctor", "list", "--root", str(tmp_path)])
    assert run_id in listed.output
    compared = RUNNER.invoke(
        app,
        [
            "forge",
            "doctor",
            "compare",
            "--baseline",
            run_id,
            "--current",
            run_id,
            "--root",
            str(tmp_path),
        ],
    )
    assert compared.exit_code == 0, compared.output
    assert '"empty": true' in compared.output


def test_cli_handoff_to_doctor_engine_declared(tmp_path: Path) -> None:
    """forge-doctor-api is a declared peer — `forge handoff --to` accepts it."""
    submit = RUNNER.invoke(
        app,
        [
            "forge",
            "submit",
            "--task-id",
            "t-doctor-1",
            "--capability",
            "api.analyze",
            "--intent",
            "handoff to doctor",
            "--root",
            str(tmp_path),
        ],
    )
    assert submit.exit_code == 0, submit.output
    handoff = RUNNER.invoke(
        app,
        [
            "forge",
            "handoff",
            "--task-id",
            "t-doctor-1",
            "--to",
            "forge-doctor-api",
            "--root",
            str(tmp_path),
        ],
    )
    assert handoff.exit_code == 0, handoff.output
    refused = RUNNER.invoke(
        app,
        [
            "forge",
            "handoff",
            "--task-id",
            "t-doctor-1",
            "--to",
            "not-a-forge",
            "--root",
            str(tmp_path),
        ],
    )
    assert "AF-FORGE-ENGINE-UNKNOWN" in refused.output
