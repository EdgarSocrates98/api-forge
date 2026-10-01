"""Git integration contract; mutation is planned, not executed here."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.platform import CapabilityRecord
from apiforge.integrations.gateway import StaticIntegrationAdapter


def local_git_adapter(root: Path) -> StaticIntegrationAdapter:
    return StaticIntegrationAdapter(
        "git",
        (
            CapabilityRecord(
                capability_id="git.plan",
                vertical="integration",
                operation="plan-git-change",
                state="unresolved",
                surfaces=("cli", "mcp", "ide", "ui"),
                evidence=(str(root),),
                limitations=("host mutation is not executed by the offline core",),
                prerequisites=("worktree", "policy", "rollback"),
                risk="local_reversible",
                rollback="restore the sandbox or worktree",
                verifier="tests/runtime/test_supervisor.py",
                documentation="docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md",
                adapter="git",
            ),
        ),
    )
