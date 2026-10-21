"""forge-doctor-api delegation lane (lf-0030, PHASE 7).

Evidence-collection only. The adapter:

1. **discovers** the doctor CLI — ``shutil.which("forge-doctor-api")`` first,
   then ``importlib.metadata.version`` as proof the package is installed in
   this interpreter (executed as ``python -m forge_doctor_api``, never
   imported — the lane is the public CLI, not doctor internals);
2. **verifies** identity — ``--version`` must answer
   ``forge-doctor-api <semver>``; presence alone is ``untrusted``;
3. **runs** ``scan <target> --format agent`` through governed argv-only exec —
   no shell, env-scrubbed (allowlist minus credential-shaped names), timeout,
   output cap;
4. **parses** the frozen line schema ``id|sev|conf|subject[:line]|desc`` plus
   ``UNKNOWN|subject|missing`` rows into structured findings, preserving
   severity and confidence verbatim;
5. **classifies** exit codes — 0 completed, 1 gate-tripped (findings still
   evidence), 2 usage refusal, anything else a named failure;
6. **publishes** a persisted ``apiforge/doctor-delegation/v1`` handoff record
   carrying the chain fields (``correlation_id``, ``visited_providers``,
   ``max_hops``) of the SpecialistDelegation semantics;
7. **compares** two persisted scans (before/after revalidation) as
   ``apiforge-derived`` — the doctor's own ``DeltaContext``/``baseline_ref``
   machinery lives on its in-process ``DoctorBoundary``, unreachable through
   the agent CLI, so the diff here is computed locally over
   (check_id, subject) keys and says so.

Never mutates: the argv template is closed and read-only — a mutation-shaped
argv (``safefix``, ``fix``, ``migrate``, ``--apply``, ``--write``, ``--out``,
``--incremental``) is refused ``AF-DELEG-READ-ONLY`` before anything spawns.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from apiforge.contracts.delegation import (
    CORRELATION_ID,
    DelegationChain,
    DelegationErrorRecord,
    DelegationFailure,
    DelegationStatus,
    DoctorDelegationRecord,
    DoctorDiscovery,
    DoctorFindingRow,
    DoctorScan,
    DoctorUnknownRow,
    ScanDelta,
    record_integrity,
)

DOCTOR_PROVIDER = "forge-doctor-api"
DOCTOR_BINARY = "forge-doctor-api"
DOCTOR_PACKAGE = "forge-doctor-api"
DOCTOR_MODULE = "forge_doctor_api"
DOCTOR_CAPABILITY = "api.scan"

# `--format agent` wraps `export_findings` — schema_version "1.x", additive-only
# within major 1 (doctor output contract); a different major is a new contract.
SUPPORTED_AGENT_SCHEMA_MAJOR = 1

STDOUT_CAP_BYTES = 8 * 1024 * 1024
STDERR_TAIL_CHARS = 300
VERSION_TIMEOUT_S = 10
DEFAULT_TIMEOUT_S = 300
DEFAULT_MAX_HOPS = 4

FAIL_ON_CATEGORIES = frozenset({"breaking", "security", "policy"})

# Tokens that would turn the read-only evidence lane into a mutation lane.
_MUTATING_TOKENS = frozenset(
    {"safefix", "fix", "migrate", "apply", "--apply", "--write", "--out", "--incremental"}
)
# Closed argv vocabulary for a scan invocation, besides the binary prefix,
# the target path and the --fail-on categories.
_SCAN_ARGV_STATIC = frozenset({"scan", "--format", "agent", "--fail-on"})

# sha256(id) pattern for minted run/correlation keys.
_VERSION_RE = re.compile(r"^forge-doctor-api\s+(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\s*$")
_HEADER_RE = re.compile(r"^#\s*schema_version=(\S+)\s+tool_version=(\S+)\s*$")
_KNOWLEDGE_RE = re.compile(r"^#\s*knowledge_versions=(.*)$")
_SUBJECT_LINE_RE = re.compile(r"^(.*):(\d+)$")


class DelegationError(ValueError):
    """A refused or failed delegation; ``str()`` begins with the AF code.

    ``failure`` is the DelegationFailure vocabulary entry the persisted
    record reports — the AF code names the refusal site, the failure code
    names the category for consumers.
    """

    def __init__(self, code: str, detail: str, *, failure: DelegationFailure) -> None:
        self.code = code
        self.failure = failure
        super().__init__(f"{code}: {detail}")


# ---------------------------------------------------------------------------
# Environment scrubbing — allowlist first, credential filter second
# ---------------------------------------------------------------------------

_ALLOWED_ENV: Mapping[str, str] = {
    "PATH": "resolve executables",
    "PATHEXT": "Windows executable extensions",
    "SYSTEMROOT": "Windows runtime",
    "SYSTEMDRIVE": "Windows system drive",
    "WINDIR": "Windows directory",
    "COMSPEC": "Windows command interpreter",
    "HOME": "POSIX home",
    "USERPROFILE": "Windows home",
    "TEMP": "temporary directory",
    "TMP": "temporary directory",
    "TMPDIR": "POSIX temporary directory",
    "LANG": "locale",
    "LC_ALL": "locale override",
}

_FORCED_ENV: Mapping[str, str] = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

_CREDENTIAL_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"^AWS_",
        r"(^|_)TOKEN(_|$)",
        r"SECRET",
        r"PASS(WORD|WD)",
        r"API_?KEY",
        r"ACCESS_?KEY",
        r"CREDENTIAL",
        r"^SSH_AUTH_SOCK$",
        r"^(AZURE|ARM|GH|CLOUDSDK|ACTIONS)_",
        r"^(KUBECONFIG|DOCKER_CONFIG|NETRC)$",
        r"_PROXY$",
    )
)

_URL_USERINFO = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^/?#\s@]+@")


def _is_credential_name(name: str) -> bool:
    return any(pattern.search(name) for pattern in _CREDENTIAL_PATTERNS)


def scrub_env(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Allowlist + credential filter — credentials never reach the doctor."""
    src = os.environ if source is None else source
    env = {
        key: value
        for key, value in src.items()
        if key.upper() in _ALLOWED_ENV
        and key.upper() not in _FORCED_ENV
        and not _is_credential_name(key)
        and not _URL_USERINFO.search(value)
    }
    env.update(_FORCED_ENV)
    return env


# ---------------------------------------------------------------------------
# Discovery — measured, never declared
# ---------------------------------------------------------------------------


def _package_version() -> str | None:
    try:
        return importlib.metadata.version(DOCTOR_PACKAGE)
    except importlib.metadata.PackageNotFoundError:
        return None


def _probe_cli_version(
    argv_prefix: Sequence[str], *, timeout: int = VERSION_TIMEOUT_S
) -> str | None:
    """Run ``<argv_prefix> --version``; parse the doctor identity, never guess."""
    try:
        proc = subprocess.run(
            [*argv_prefix, "--version"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=scrub_env(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    first = (proc.stdout or "").strip().splitlines()
    if not first:
        return None
    match = _VERSION_RE.match(first[0].strip())
    return match.group(1) if match else None


def discover_doctor(
    *,
    which: Callable[[str], str | None] = shutil.which,
    package_version: Callable[[], str | None] = _package_version,
    probe: Callable[[Sequence[str]], str | None] = _probe_cli_version,
) -> DoctorDiscovery:
    """Measure doctor presence: binary → package → verified identity.

    States: ``absent`` (nothing found), ``untrusted`` (found but identity
    unproven — version probe failed or did not name the doctor), ``verified``
    (``--version`` answers ``forge-doctor-api <semver>``).
    """
    binary = which(DOCTOR_BINARY)
    pkg_version = package_version()
    argv_prefix: tuple[str, ...]
    detail = ""
    if binary is not None:
        argv_prefix = (binary,)
    elif pkg_version is not None:
        argv_prefix = (sys.executable, "-m", DOCTOR_MODULE)
        detail = "CLI absent from PATH; package importable — invoked as python -m"
    else:
        return DoctorDiscovery(
            state="absent",
            detail="forge-doctor-api binary not on PATH and package not installed",
        )
    cli_version = probe(argv_prefix)
    if cli_version is None:
        return DoctorDiscovery(
            state="untrusted",
            binary=binary,
            argv_prefix=argv_prefix,
            package_version=pkg_version,
            detail=detail or "--version did not answer 'forge-doctor-api <semver>'",
        )
    return DoctorDiscovery(
        state="verified",
        binary=binary,
        argv_prefix=argv_prefix,
        cli_version=cli_version,
        package_version=pkg_version,
        detail=detail,
    )


# ---------------------------------------------------------------------------
# Closed argv template — read-only by construction
# ---------------------------------------------------------------------------


def doctor_scan_argv(
    argv_prefix: Sequence[str],
    target: Path | str,
    *,
    fail_on: Sequence[str] = (),
) -> list[str]:
    """The fixed scan argv — visible, closed, read-only."""
    unknown = sorted(set(fail_on) - FAIL_ON_CATEGORIES)
    if unknown:
        raise DelegationError(
            "AF-DELEG-INVALID-INPUT",
            f"--fail-on categories {unknown} not in {sorted(FAIL_ON_CATEGORIES)}",
            failure="invalid-input",
        )
    argv = [*argv_prefix, "scan", str(target), "--format", "agent"]
    if fail_on:
        argv += ["--fail-on", ",".join(sorted(set(fail_on)))]
    _assert_read_only(argv, argv_prefix=argv_prefix, target=str(target), fail_on=fail_on)
    return argv


def _assert_read_only(
    argv: Sequence[str],
    *,
    argv_prefix: Sequence[str],
    target: str,
    fail_on: Sequence[str] = (),
) -> None:
    """Closed-template guard: anything outside the read-only scan shape is
    refused — this lane never mutates, and doctor never modifies code through
    this flow."""
    rest = list(argv[len(argv_prefix) :])
    allowed = set(_SCAN_ARGV_STATIC) | {target} | set(fail_on)
    if fail_on:
        allowed.add(",".join(sorted(set(fail_on))))
    for token in rest:
        if token in _MUTATING_TOKENS or (token.startswith("-") and token not in allowed):
            raise DelegationError(
                "AF-DELEG-READ-ONLY",
                f"argv token {token!r} is outside the read-only scan template — "
                "the delegation lane collects evidence and never mutates",
                failure="policy-refusal",
            )
    if not rest or rest[0] != "scan" or "--format" not in rest or "agent" not in rest:
        raise DelegationError(
            "AF-DELEG-READ-ONLY",
            f"argv {list(argv)!r} is not the closed `scan <target> --format agent` "
            "template — refused before spawn",
            failure="policy-refusal",
        )


# ---------------------------------------------------------------------------
# `--format agent` parser — strict, frozen line schema
# ---------------------------------------------------------------------------


def _split_subject(subject: str) -> tuple[str, int | None]:
    match = _SUBJECT_LINE_RE.match(subject)
    if match:
        return match.group(1) or "-", int(match.group(2))
    return subject or "-", None


def parse_agent_output(
    text: str,
) -> tuple[dict[str, Any], list[DoctorFindingRow], list[DoctorUnknownRow]]:
    """Parse doctor agent output; strict — malformed input is a named refusal.

    Schema 1.x is additive-only on the doctor side: extra trailing ``|``
    fields are tolerated inside the description (``split("|", 4)``); a
    different schema major is ``AF-DELEG-INCOMPATIBLE``.
    """
    lines = text.splitlines()
    meta: dict[str, Any] = {"schema_version": None, "tool_version": None, "knowledge_versions": {}}
    findings: list[DoctorFindingRow] = []
    unknowns: list[DoctorUnknownRow] = []
    header_seen = False
    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        if line.startswith("#"):
            header = _HEADER_RE.match(line)
            if header and not header_seen:
                meta["schema_version"] = header.group(1)
                meta["tool_version"] = header.group(2)
                header_seen = True
                continue
            knowledge = _KNOWLEDGE_RE.match(line)
            if knowledge:
                for pair in knowledge.group(1).split(","):
                    name, _, version = pair.partition("@")
                    if name.strip():
                        meta["knowledge_versions"][name.strip()] = version.strip()
                continue
            raise DelegationError(
                "AF-DELEG-INVALID-OUTPUT",
                f"line {lineno}: unrecognized comment row {line[:80]!r}",
                failure="invalid-output",
            )
        if line.startswith("UNKNOWN|"):
            parts = line.split("|", 2)
            if len(parts) != 3 or not parts[1]:
                raise DelegationError(
                    "AF-DELEG-INVALID-OUTPUT",
                    f"line {lineno}: malformed UNKNOWN row {line[:80]!r}",
                    failure="invalid-output",
                )
            unknowns.append(DoctorUnknownRow(subject=parts[1], missing=parts[2]))
            continue
        parts = line.split("|", 4)
        if len(parts) != 5 or not parts[0]:
            raise DelegationError(
                "AF-DELEG-INVALID-OUTPUT",
                f"line {lineno}: expected id|sev|conf|subject[:line]|desc, got {line[:80]!r}",
                failure="invalid-output",
            )
        subject, line_no = _split_subject(parts[3])
        findings.append(
            DoctorFindingRow(
                check_id=parts[0],
                severity=parts[1],
                confidence=parts[2],
                subject=subject,
                line=line_no,
                description=parts[4],
            )
        )
    if not header_seen:
        raise DelegationError(
            "AF-DELEG-INVALID-OUTPUT",
            "missing '# schema_version=<v> tool_version=<v>' header — "
            "not a doctor --format agent payload",
            failure="invalid-output",
        )
    major = str(meta["schema_version"]).split(".", 1)[0]
    if not major.isdigit() or int(major) != SUPPORTED_AGENT_SCHEMA_MAJOR:
        raise DelegationError(
            "AF-DELEG-INCOMPATIBLE",
            f"agent schema_version {meta['schema_version']!r} unsupported — "
            f"expected major {SUPPORTED_AGENT_SCHEMA_MAJOR} (additive-only v1)",
            failure="version-incompatible",
        )
    return meta, findings, unknowns


# ---------------------------------------------------------------------------
# Governed run — policy gate, argv-only exec, exit-code classification
# ---------------------------------------------------------------------------


def _gate(target: Path, policy: Any = None) -> None:
    """Policy decides before anything spawns; a non-allow is a named refusal."""
    from apiforge.policy.decide import ActionRequest, decide
    from apiforge.policy.loader import load_policy

    decision = decide(
        policy if policy is not None else load_policy(),
        ActionRequest(
            verb="delegation.doctor.scan",
            autonomy_class="read_only",
            target=str(target),
        ),
    )
    if decision.outcome != "allow":
        missing = ", ".join(decision.missing_requirements) or (decision.reason_code or "policy")
        raise DelegationError(
            "AF-DELEG-POLICY",
            f"delegation.doctor.scan on {target} — {decision.outcome}: {missing}",
            failure="policy-refusal",
        )


def run_doctor_scan(
    target: Path,
    *,
    argv_prefix: Sequence[str],
    fail_on: Sequence[str] = (),
    timeout: int = DEFAULT_TIMEOUT_S,
    run_id: str = "drun",
    env: Mapping[str, str] | None = None,
) -> DoctorScan:
    """Run `scan <target> --format agent` and parse the output.

    Exit codes: 0 → completed; 1 → completed with the doctor's gate tripped
    (the report is identical — findings are still evidence); 2 → doctor
    usage refusal; any other nonzero → runtime failure.
    """
    argv = doctor_scan_argv(argv_prefix, target, fail_on=fail_on)
    started = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=scrub_env(env),
        )
    except subprocess.TimeoutExpired as exc:
        raise DelegationError(
            "AF-DELEG-TIMEOUT",
            f"forge-doctor-api scan exceeded {timeout}s on {target}",
            failure="timeout",
        ) from exc
    except OSError as exc:
        raise DelegationError(
            "AF-DELEG-FAILED",
            f"could not spawn {argv[0]}: {exc}",
            failure="runtime-error",
        ) from exc
    elapsed_ms = int((time.monotonic() - started) * 1000)
    stdout = proc.stdout or ""
    if len(stdout.encode("utf-8", errors="replace")) > STDOUT_CAP_BYTES:
        raise DelegationError(
            "AF-DELEG-OUTPUT-LIMIT",
            f"doctor stdout exceeds the {STDOUT_CAP_BYTES}-byte cap — "
            "evidence is never silently truncated",
            failure="invalid-output",
        )
    stdout_sha = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
    stderr_tail = (proc.stderr or "").strip()[-STDERR_TAIL_CHARS:]
    if proc.returncode == 2:
        raise DelegationError(
            "AF-DELEG-USAGE",
            f"doctor refused the invocation (exit 2): {stderr_tail or 'usage error'}",
            failure="invalid-input",
        )
    if proc.returncode not in (0, 1):
        raise DelegationError(
            "AF-DELEG-FAILED",
            f"doctor exited {proc.returncode}: {stderr_tail or 'no stderr'}",
            failure="runtime-error",
        )
    meta, findings, unknowns = parse_agent_output(stdout)
    return DoctorScan(
        run_id=run_id,
        target=str(target),
        argv=tuple(argv),
        exit_code=proc.returncode,
        gate_failed=proc.returncode == 1,
        tool_version=meta["tool_version"],
        scan_schema_version=meta["schema_version"],
        knowledge_versions=dict(meta["knowledge_versions"]),
        findings=tuple(findings),
        unknowns=tuple(unknowns),
        stdout_sha256=stdout_sha,
        stderr_tail=stderr_tail,
        elapsed_ms=elapsed_ms,
    )


# ---------------------------------------------------------------------------
# Chain admission — SpecialistDelegation chain semantics, natively
# ---------------------------------------------------------------------------


def mint_chain(
    *, correlation_id: str, max_hops: int = DEFAULT_MAX_HOPS, timeout_budget_s: int = 600
) -> DelegationChain:
    """The consumer mints the chain: api-forge is the first visited provider."""
    return DelegationChain(
        correlation_id=correlation_id,
        delegation_depth=0,
        visited_providers=("api-forge",),
        max_hops=max_hops,
        timeout_budget_s=timeout_budget_s,
    )


def admit_hop(chain: DelegationChain, provider: str, *, cost_s: int = 0) -> DelegationChain:
    """Advance the chain one hop — cycle/budget/cancel refused at admission."""
    if chain.cancelled:
        raise DelegationError(
            "AF-DELEG-CANCELLED",
            "delegation chain is cancelled — no further hops",
            failure="cancelled",
        )
    if provider in chain.visited_providers:
        raise DelegationError(
            "AF-DELEG-CYCLE",
            f"{provider!r} already in visited_providers {list(chain.visited_providers)}",
            failure="cycle-detected",
        )
    if chain.delegation_depth + 1 > chain.max_hops:
        raise DelegationError(
            "AF-DELEG-BUDGET",
            f"depth {chain.delegation_depth + 1} exceeds max_hops {chain.max_hops}",
            failure="budget-exhausted",
        )
    if cost_s and cost_s >= chain.timeout_budget_s:
        raise DelegationError(
            "AF-DELEG-BUDGET",
            f"scan budget {cost_s}s exceeds remaining chain budget {chain.timeout_budget_s}s",
            failure="budget-exhausted",
        )
    return DelegationChain(
        correlation_id=chain.correlation_id,
        delegation_depth=chain.delegation_depth + 1,
        visited_providers=(*chain.visited_providers, provider),
        max_hops=chain.max_hops,
        timeout_budget_s=chain.timeout_budget_s - cost_s,
        cancelled=chain.cancelled,
    )


# ---------------------------------------------------------------------------
# Before/after — apiforge-derived delta over persisted scans
# ---------------------------------------------------------------------------


def _finding_key(row: DoctorFindingRow) -> str:
    return f"{row.check_id}|{row.subject}"


def compare_scans(baseline: DoctorScan, current: DoctorScan) -> ScanDelta:
    """Diff two parsed scans — deterministic, reorder-proof."""
    prev = {_finding_key(f): f for f in baseline.findings}
    cur = {_finding_key(f): f for f in current.findings}
    added = sorted(set(cur) - set(prev))
    removed = sorted(set(prev) - set(cur))
    changed = sorted(
        key
        for key in set(prev) & set(cur)
        if (prev[key].severity, prev[key].confidence, prev[key].description, prev[key].line)
        != (cur[key].severity, cur[key].confidence, cur[key].description, cur[key].line)
    )
    severity_changes = sorted(
        f"{key}: {prev[key].severity}->{cur[key].severity}"
        for key in changed
        if prev[key].severity != cur[key].severity
    )
    confidence_changes = sorted(
        f"{key}: {prev[key].confidence}->{cur[key].confidence}"
        for key in changed
        if prev[key].confidence != cur[key].confidence
    )
    prev_u = {f"{u.subject}|{u.missing}" for u in baseline.unknowns}
    cur_u = {f"{u.subject}|{u.missing}" for u in current.unknowns}
    return ScanDelta(
        baseline_ref=baseline.run_id,
        current_ref=current.run_id,
        delta_source="apiforge-derived",
        findings_added=tuple(added),
        findings_removed=tuple(removed),
        findings_changed=tuple(changed),
        severity_changes=tuple(severity_changes),
        confidence_changes=tuple(confidence_changes),
        unknowns_added=tuple(sorted(cur_u - prev_u)),
        unknowns_removed=tuple(sorted(prev_u - cur_u)),
        empty=not (added or removed or changed or (cur_u - prev_u) or (prev_u - cur_u)),
    )


# ---------------------------------------------------------------------------
# Orchestration — discover → verify → gate → run → record → persist
# ---------------------------------------------------------------------------


def _mint_ids(
    correlation_id: str | None, target: Path, argv_prefix: Sequence[str]
) -> tuple[str, str, str]:
    created = datetime.now(UTC).isoformat()
    corr = correlation_id or f"corr-{hashlib.sha256(created.encode()).hexdigest()[:16]}"
    if not CORRELATION_ID.match(corr):
        raise DelegationError(
            "AF-DELEG-INVALID-INPUT",
            f"correlation_id {corr!r} must match {CORRELATION_ID.pattern}",
            failure="invalid-input",
        )
    idem_src = json.dumps(
        {
            "provider": DOCTOR_PROVIDER,
            "capability": DOCTOR_CAPABILITY,
            "target": str(target),
            "argv_prefix": list(argv_prefix),
            "correlation_id": corr,
        },
        sort_keys=True,
    )
    idem = f"idem-{hashlib.sha256(idem_src.encode()).hexdigest()[:24]}"
    run = f"drun-{hashlib.sha256((idem_src + created).encode()).hexdigest()[:16]}"
    return run, corr, idem


_REFUSED_FAILURES = frozenset(
    {
        "provider-absent",
        "version-incompatible",
        "invalid-input",
        "permission-denied",
        "policy-refusal",
        "cycle-detected",
        "budget-exhausted",
        "cancelled",
    }
)


def _refused_record(
    *,
    run_id: str,
    correlation_id: str,
    idempotency_key: str,
    chain: DelegationChain,
    discovery: DoctorDiscovery | None,
    target: Path,
    exc: DelegationError,
) -> DoctorDelegationRecord:
    """Evidence of a refusal: ``refused`` when nothing executed, ``failed``
    when the doctor ran and failed."""
    record = DoctorDelegationRecord(
        run_id=run_id,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        source_version=(discovery.cli_version if discovery else None) or "unknown",
        status="refused" if exc.failure in _REFUSED_FAILURES else "failed",
        discovery_state=discovery.state if discovery else None,
        input_refs=(f"target:{target}",),
        error=DelegationErrorRecord(
            code=exc.failure,
            detail=str(exc).split(": ", 1)[-1][:500],
            retryable=exc.failure in ("timeout", "runtime-error"),
        ),
        chain=chain,
        created_at=datetime.now(UTC).isoformat(),
    )
    return record.model_copy(update={"integrity": record_integrity(record)})


def delegate_doctor_scan(
    root: Path,
    target: Path,
    *,
    correlation_id: str | None = None,
    chain: DelegationChain | None = None,
    fail_on: Sequence[str] = (),
    timeout: int = DEFAULT_TIMEOUT_S,
    max_hops: int = DEFAULT_MAX_HOPS,
    allow_unverified: bool = False,
    policy: Any = None,
    discovery: DoctorDiscovery | None = None,
    env: Mapping[str, str] | None = None,
) -> DoctorDelegationRecord:
    """The PHASE 7 evidence step: gate → chain → discover → verify → scan → record.

    Every refusal persists a ``refused`` record before raising — the store is
    the evidence trail, never a silent failure. Returns the persisted
    ``completed``/``partial`` record.
    """
    from apiforge.forge import store

    root = Path(root)
    target = Path(target)
    discovered = discovery
    run_id, corr, idem = _mint_ids(correlation_id, target, ())
    base_chain = chain or mint_chain(
        correlation_id=corr,
        max_hops=max_hops,
        timeout_budget_s=max(timeout + 1, 60),
    )

    try:
        if not target.is_dir():
            raise DelegationError(
                "AF-DELEG-TARGET",
                f"scan target {target} is not a directory",
                failure="invalid-input",
            )
        _gate(target, policy)
        admitted = admit_hop(base_chain, DOCTOR_PROVIDER, cost_s=timeout)
        discovered = discovered or discover_doctor()
        if discovered.state == "absent":
            raise DelegationError(
                "AF-DELEG-ABSENT",
                "forge-doctor-api not found — install it "
                "(pip install forge-doctor-api) or add its CLI to PATH",
                failure="provider-absent",
            )
        if discovered.state != "verified" and not allow_unverified:
            raise DelegationError(
                "AF-DELEG-INCOMPATIBLE",
                f"doctor discovered but unverified ({discovered.detail}) — "
                "pass --allow-unverified to run against an unproven identity",
                failure="version-incompatible",
            )
        run_id, corr, idem = _mint_ids(correlation_id, target, discovered.argv_prefix)
        admitted = admitted.model_copy(update={"correlation_id": corr})
        scan = run_doctor_scan(
            target,
            argv_prefix=discovered.argv_prefix,
            fail_on=fail_on,
            timeout=timeout,
            run_id=run_id,
            env=env,
        )
    except DelegationError as exc:
        store.write_delegation(
            root,
            _refused_record(
                run_id=run_id,
                correlation_id=corr,
                idempotency_key=idem,
                chain=base_chain,
                discovery=discovered,
                target=target,
                exc=exc,
            ),
        )
        raise

    created = datetime.now(UTC).isoformat()
    limitations: list[str] = [
        (
            "evidence collection only — plan/implement stay with the host; the "
            "doctor is deterministic diagnostics, api-forge owns the changes"
        ),
        (
            "severity/confidence are the doctor's declared tokens, verbatim — "
            "not apiforge Severity/FindingStatus values"
        ),
    ]
    if scan.gate_failed:
        limitations.append("doctor gate tripped (exit 1) — findings are still evidence")
    if discovered.state != "verified":
        limitations.append("doctor identity unverified — --allow-unverified accepted the risk")
    if discovered.binary is None and discovered.argv_prefix:
        limitations.append("doctor invoked as python -m forge_doctor_api — CLI not on PATH")
    status: DelegationStatus = "partial" if (scan.unknowns or scan.gate_failed) else "completed"
    record = DoctorDelegationRecord(
        run_id=run_id,
        correlation_id=corr,
        idempotency_key=idem,
        source_version=scan.tool_version or discovered.cli_version or "unknown",
        status=status,
        discovery_state=discovered.state,
        input_refs=(f"target:{target}", "argv:" + " ".join(scan.argv)),
        result_refs=(),
        findings=scan.findings,
        unknowns=scan.unknowns,
        limitations=tuple(limitations),
        chain=admitted,
        elapsed_ms=scan.elapsed_ms,
        created_at=created,
    )
    record = record.model_copy(update={"integrity": record_integrity(record)})
    directory = store.write_delegation(root, record)
    (directory / "scan.agent.txt").write_text(_read_scan_stdout_hint(scan), encoding="utf-8")
    (directory / "scan.json").write_text(scan.model_dump_json(indent=2), encoding="utf-8")
    refs = (
        f".apiforge/forge/delegations/{run_id}/scan.agent.txt#sha256:{scan.stdout_sha256[:12]}",
        f".apiforge/forge/delegations/{run_id}/scan.json",
    )
    record = record.model_copy(update={"result_refs": refs})
    record = record.model_copy(update={"integrity": record_integrity(record)})
    store.rewrite_delegation(root, record)
    return record


def _read_scan_stdout_hint(scan: DoctorScan) -> str:
    """Rebuild the evidence view of stdout: parsed rows verbatim, never the
    raw stream (the raw stream is bounded by STDOUT_CAP and hashed on the
    scan record; artifacts keep the parsed projection)."""
    lines = [
        f"# schema_version={scan.scan_schema_version} tool_version={scan.tool_version}",
        "# knowledge_versions="
        + ",".join(f"{k}@{v}" for k, v in sorted(scan.knowledge_versions.items())),
    ]
    for f in scan.findings:
        lines.append(
            f"{f.check_id}|{f.severity}|{f.confidence}|{f.subject}"
            f"{':' + str(f.line) if f.line else ''}|{f.description}"
        )
    for u in scan.unknowns:
        lines.append(f"UNKNOWN|{u.subject}|{u.missing}")
    return "\n".join(lines) + "\n"


def load_delegation_scan(root: Path, run_id: str) -> DoctorScan:
    """Load the parsed scan of a persisted run — the compare input."""
    from apiforge.forge import store

    path = store.delegation_dir(root, run_id) / "scan.json"
    if not path.is_file():
        raise DelegationError(
            "AF-DELEG-NOT-FOUND",
            f"no scan.json for delegation {run_id!r} under {root} — "
            "a refused delegation carries no scan",
            failure="invalid-input",
        )
    try:
        return DoctorScan.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise DelegationError("AF-DELEG-STORE", f"{path}: {exc}", failure="invalid-output") from exc


def compare_delegations(root: Path, baseline_run: str, current_run: str) -> ScanDelta:
    """Before/after revalidation: baseline scan vs current scan.

    The revalidation loop of PHASE 7: coordinator delegates a scan, the host
    plans/implements, doctor is re-run, and this compare names what the delta
    changed. ``delta_source`` is ``apiforge-derived`` — the doctor's own
    DeltaContext is not reachable through `scan --format agent`.
    """
    baseline = load_delegation_scan(root, baseline_run)
    current = load_delegation_scan(root, current_run)
    delta = compare_scans(baseline, current)
    from apiforge.forge import store

    directory = store.delegation_dir(root, current_run)
    (directory / f"compare-{baseline_run}.json").write_text(
        delta.model_dump_json(indent=2), encoding="utf-8"
    )
    return delta


__all__ = [
    "DEFAULT_MAX_HOPS",
    "DEFAULT_TIMEOUT_S",
    "DOCTOR_BINARY",
    "DOCTOR_CAPABILITY",
    "DOCTOR_PACKAGE",
    "DOCTOR_PROVIDER",
    "FAIL_ON_CATEGORIES",
    "STDOUT_CAP_BYTES",
    "SUPPORTED_AGENT_SCHEMA_MAJOR",
    "DelegationError",
    "admit_hop",
    "compare_delegations",
    "compare_scans",
    "delegate_doctor_scan",
    "discover_doctor",
    "doctor_scan_argv",
    "load_delegation_scan",
    "mint_chain",
    "parse_agent_output",
    "run_doctor_scan",
    "scrub_env",
]
