"""Offline Devin payloads and local capability observations.

This module deliberately stops at payload generation and local executable
discovery.  It never calls Devin's API, starts a Devin session, changes a
repository, or opens a pull request.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.devin import (
    DevinCheck,
    DevinCliProbe,
    DevinLaunch,
    DevinPayload,
    DevinPermissionMode,
    DevinSurface,
    DevinTaskKind,
)
from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.host import HostCapability, HostDeclaration, SupportState

DEVIN_DOCS = (
    "https://docs.devin.ai/cli/extensibility",
    "https://docs.devin.ai/cli/reference/commands",
    "https://docs.devin.ai/cli/reference/permissions",
)

_DEFAULT_PROHIBITIONS = (
    "Do not run git reset --hard, git checkout --, or git clean -fd.",
    "Do not force-push, merge, deploy, or create a PR from the agent core.",
    "Do not invent evidence, versions, production health, cost, or throughput.",
    "Do not place credentials in committed files or payloads.",
)


def _checks(task_kind: DevinTaskKind) -> tuple[DevinCheck, ...]:
    checks = [
        DevinCheck(
            name="diff-check",
            command="git diff --check",
            purpose="detect whitespace and patch-format errors",
        ),
        DevinCheck(
            name="focused-tests",
            command="python -m pytest -q",
            purpose="run the focused or full local test suite selected by the task",
        ),
    ]
    if task_kind in {"implementation", "verification", "review", "handoff"}:
        checks.extend(
            (
                DevinCheck(
                    name="ruff",
                    command="ruff check src tests",
                    purpose="lint project-owned Python code without widening scope to vendor or legacy scripts",
                ),
                DevinCheck(
                    name="mypy",
                    command="mypy src/apiforge",
                    purpose="verify strict typing for the package",
                ),
            )
        )
    if task_kind in {"discovery", "planning"}:
        checks.insert(
            0,
            DevinCheck(
                name="routing",
                command=(
                    "apiforge next-step --findings .apiforge/case/findings.json "
                    "--phase discover"
                ),
                purpose="route from persisted findings before selecting a specialist",
            ),
        )
    return tuple(checks)


def _prompt(
    *,
    objective: str,
    task_kind: DevinTaskKind,
    root: Path,
    case_path: str,
) -> str:
    phase = {
        "discovery": "discover",
        "planning": "intent -> contract -> architecture -> plan",
        "implementation": "build",
        "verification": "verify -> secure -> benchmark",
        "review": "verify",
        "handoff": "ship",
    }[task_kind]
    return f"""You are Devin working on API Forge in {root}.

Objective:
{objective.strip()}

API Forge operating contract:
1. Read AGENT_PROTOCOL.md and AGENTS.md before substantive work.
2. Load or create the persisted case under {case_path}.
3. Run `apiforge next-step` before selecting a specialist whenever findings exist.
4. Follow the SDD route and start at the requested phase: {phase}.
5. Prefer deterministic facts, rules, indexes, Graphify and read-only adapters.
6. Keep external integrations read-only; the CI green-validation workflow is the
   only permitted path for a repository PR mutation.
7. Preserve fact_ids, AF-* codes, errors, warnings, failed tests and unresolved
   gaps. Never convert a declaration into observed or verified evidence.
8. Do not claim DONE without independent verification and an Outcome Brief.

Required response shape:
Status:
Outcome:
Human action:
Proof:
Gaps:
Next:
Open:

Return file paths, commands, exact results and unresolved items. Do not ask for
or print credentials. Stop and report the blocking AF-* code when a required
policy, evidence source or approval is unavailable."""


def _launch(
    *,
    surface: DevinSurface,
    permission_mode: DevinPermissionMode,
    sandbox: bool,
    model: str | None,
    task_kind: DevinTaskKind,
) -> DevinLaunch:
    args: list[str] = []
    slash_commands: list[str] = []
    if surface in {"cli", "cloud"}:
        if surface == "cloud":
            args.append("--cloud")
        if permission_mode != "normal":
            args.extend(("--permission-mode", permission_mode))
        if sandbox:
            args.append("--sandbox")
        if model:
            args.extend(("--model", model))
    if task_kind in {"planning", "review"}:
        slash_commands.append("/plan")
    if task_kind == "handoff":
        slash_commands.append("/handoff")

    if surface == "desktop":
        return DevinLaunch(
            surface=surface,
            executable="Devin Desktop",
            prompt_transport="desktop-paste",
            slash_commands=tuple(slash_commands),
            operator_steps=(
                "Open the repository in Devin Desktop.",
                "Paste the generated prompt into Agent Command Center.",
                "Inspect the diff and evidence before accepting any write.",
            ),
        )
    if surface == "cloud":
        return DevinLaunch(
            surface=surface,
            args=tuple(args),
            prompt_transport="positional",
            slash_commands=tuple(slash_commands),
            operator_steps=(
                "Run `devin --cloud` from the repository context or use `/handoff`.",
                "Select the repository and platform explicitly.",
                "Use `/open desktop` or `/pickup` only after reviewing the cloud result.",
            ),
        )
    return DevinLaunch(
        surface=surface,
        args=tuple(args),
        prompt_transport="positional",
        slash_commands=tuple(slash_commands),
        operator_steps=(
            "Run `devin <args> -- <prompt>` from the repository root.",
            "For automation, use `-p` or `--prompt-file` and keep workspace trust enabled.",
            "Use `/export` or `--export` when a transcript is needed as evidence.",
        ),
    )


def build_devin_payload(
    *,
    objective: str,
    surface: DevinSurface = "cli",
    task_kind: DevinTaskKind = "planning",
    root: Path = Path("."),
    title: str | None = None,
    permission_mode: DevinPermissionMode = "normal",
    sandbox: bool = False,
    model: str | None = None,
    platform: str = "unknown",
) -> DevinPayload:
    """Build a safe, portable Devin payload without contacting Devin."""
    if not objective.strip():
        raise ContractError("AF-DEVIN-OBJECTIVE", "objective must not be empty")
    if sandbox and surface == "cli" and platform.lower() == "windows":
        raise ContractError(
            "AF-DEVIN-SANDBOX-UNAVAILABLE",
            "native Windows cannot run Devin CLI --sandbox; use WSL 2 or omit sandbox",
        )
    root_path = Path(root)
    case_path = str(root_path / ".apiforge" / "case")
    launch = _launch(
        surface=surface,
        permission_mode=permission_mode,
        sandbox=sandbox,
        model=model,
        task_kind=task_kind,
    )
    return DevinPayload(
        surface=surface,
        task_kind=task_kind,
        title=title or f"API Forge {task_kind}: {objective.strip()[:72]}",
        objective=objective.strip(),
        prompt=_prompt(
            objective=objective,
            task_kind=task_kind,
            root=root_path,
            case_path=case_path,
        ),
        working_directory=str(root_path),
        case_path=case_path,
        launch=launch,
        permission_mode=permission_mode,
        sandbox=sandbox,
        model=model,
        expected_outputs=(
            "changed files or an explicit no-change result",
            "commands and exact verification results",
            "evidence references and unresolved gaps",
            "Outcome Brief using the API Forge handoff shape",
        ),
        checks=_checks(task_kind),
        prohibited_actions=_DEFAULT_PROHIBITIONS,
        requires_human_confirmation=(
            permission_mode in {"normal", "accept-edits", "smart"}
            or surface in {"desktop", "cloud"}
        ),
        evidence=EvidenceRecord(
            level="declared",
            source="apiforge.integrations.devin",
            refs=DEVIN_DOCS,
            limitations=(
                "payload generation does not prove Devin is installed or authenticated",
                "Desktop and Cloud availability are organization/account dependent",
            ),
        ),
        evidence_level="declared",
    )


def probe_devin_cli(*, env: dict[str, str] | None = None) -> DevinCliProbe:
    """Observe a local ``devin`` executable, without network or repository writes."""
    executable = shutil.which("devin")
    if executable is None:
        return DevinCliProbe(
            installed=False,
            evidence=EvidenceRecord(
                level="observed",
                source="shutil.which(devin)",
                refs=DEVIN_DOCS,
                limitations=("executable not found on PATH",),
            ),
            evidence_level="observed",
        )
    try:
        completed = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
            env=env or os.environ.copy(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return DevinCliProbe(
            installed=True,
            executable=executable,
            error=str(exc),
            evidence=EvidenceRecord(
                level="observed",
                source="devin --version",
                refs=DEVIN_DOCS,
                limitations=("version probe did not complete",),
            ),
            evidence_level="observed",
        )
    version = (completed.stdout or completed.stderr).strip().splitlines()[0:1]
    return DevinCliProbe(
        installed=completed.returncode == 0,
        executable=executable,
        cli_version=version[0] if version else None,
        error=None if completed.returncode == 0 else (completed.stderr.strip() or "version probe failed"),
        evidence=EvidenceRecord(
            level="observed",
            source="devin --version",
            refs=DEVIN_DOCS,
            limitations=() if completed.returncode == 0 else ("non-zero version probe",),
        ),
        evidence_level="observed",
    )


def build_devin_declaration(root: Path = Path(".")) -> HostDeclaration:
    """Build a declared-vs-observed Devin host declaration for negotiation."""
    probe = probe_devin_cli()
    cli_state: SupportState = "supported" if probe.installed else "unresolved"
    cli_evidence = probe.evidence
    capabilities = (
        HostCapability(
            capability="devin-payloads",
            state="supported",
            prerequisites=("AGENT_PROTOCOL.md", "AGENTS.md", ".apiforge/case"),
            evidence=EvidenceRecord(level="observed", source="repository-layout"),
            evidence_level="observed",
        ),
        HostCapability(
            capability="devin-cli",
            state=cli_state,
            prerequisites=("Devin CLI installed and authenticated",),
            limits=() if probe.installed else ("local executable was not observed",),
            evidence=cli_evidence,
            evidence_level=probe.evidence_level,
        ),
        HostCapability(
            capability="devin-desktop",
            state="supported",
            prerequisites=("Devin Desktop installed",),
            limits=("installation and account state are not locally verified",),
            evidence=EvidenceRecord(level="declared", source="official Devin Desktop documentation", refs=DEVIN_DOCS),
            evidence_level="declared",
        ),
        HostCapability(
            capability="devin-cloud-handoff",
            state="supported",
            prerequisites=("Devin account", "repository access", "explicit human review"),
            limits=("Cloud session execution is outside the offline API Forge core",),
            evidence=EvidenceRecord(level="declared", source="official Devin CLI documentation", refs=DEVIN_DOCS),
            evidence_level="declared",
        ),
        HostCapability(
            capability="devin-extensibility",
            state="supported",
            prerequisites=(".devin/ configuration",),
            evidence=EvidenceRecord(level="observed", source="repository-layout", refs=DEVIN_DOCS),
            evidence_level="observed",
        ),
    )
    return HostDeclaration(
        host="devin",
        adapter_version="devin-payload-v1",
        capabilities=capabilities,
        evidence=EvidenceRecord(
            level="declared",
            source=str(Path(root) / ".devin"),
            refs=DEVIN_DOCS,
            limitations=(
                "official product capabilities are declarations until locally observed",
            ),
        ),
        evidence_level="declared",
    )


__all__ = [
    "build_devin_declaration",
    "build_devin_payload",
    "probe_devin_cli",
]
