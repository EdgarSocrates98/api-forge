"""Approval-gated host activation plans; this module never edits user config."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field

from apiforge.agentops.parity import audit_host_parity
from apiforge.contracts.base import VersionedContract


class ActivationPlan(VersionedContract):
    host: Literal["claude", "gpt-codex", "devin", "copilot"]
    ready_for_core: bool
    repository_artifacts: tuple[str, ...]
    optional_actions: tuple[str, ...]
    limitations: tuple[str, ...]
    mutation_required: bool = True
    approval_required: bool = True
    execution_mode: Literal["plan_only"] = "plan_only"
    missing: tuple[str, ...] = ()
    risk: Literal["low", "medium", "high"] = "medium"
    evidence: tuple[str, ...] = Field(default_factory=tuple)


def build_activation_plan(host: str, root: str) -> ActivationPlan:
    if host not in {"claude", "gpt-codex", "devin", "copilot"}:
        raise ValueError(f"AF-HOST-ACTIVATION-HOST: unsupported host {host!r}")
    parity = audit_host_parity(Path(root))
    item = parity["hosts"][host]  # type: ignore[index]
    host_data = item if isinstance(item, dict) else {}
    artifacts = {
        "claude": (
            "CLAUDE.md",
            ".claude/skills",
            ".claude/agents",
            "vendor/caveman/plugins/caveman",
        ),
        "gpt-codex": ("AGENTS.md", ".agents/skills", ".agents/agents", "vendor/caveman/.codex"),
        "devin": ("AGENTS.md", ".devin/skills", "vendor/caveman/skills"),
        "copilot": ("AGENTS.md", ".github/skills", "vendor/caveman/skills"),
    }[host]
    actions = {
        "claude": ("review and optionally run the vendored Claude hook installer",),
        "gpt-codex": ("register project instructions in the Codex host",),
        "devin": ("register AGENTS.md and Devin skill directory",),
        "copilot": ("register AGENTS.md and GitHub skill directory",),
    }[host]
    limitations = tuple(host_data.get("limitations", ()))
    missing = tuple(host_data.get("missing", ()))
    return ActivationPlan(
        host=host,  # type: ignore[arg-type]
        ready_for_core=bool(host_data.get("ready_for_core", False)),
        repository_artifacts=artifacts,
        optional_actions=actions,
        limitations=limitations,
        missing=missing,
        risk="high" if host == "claude" else "medium",
        evidence=("agentops parity", "manifest:vendor/MANIFEST.sha256", "mutation:none"),
    )
