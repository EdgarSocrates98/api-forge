"""Offline installation and optional-capability diagnostics."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Literal

from apiforge.contracts.base import ContractError
from apiforge.contracts.distribution import CapabilityDiagnostic, DistributionDoctor
from apiforge.contracts.evidence import EvidenceRecord
from apiforge.distribution.assets import asset_status
from apiforge.distribution.paths import resolve_paths


def _writable(path: Path) -> bool:
    if path.exists():
        return os.access(path, os.W_OK)
    return os.access(path.parent, os.W_OK)


def diagnose(
    cwd: Path | None = None,
    *,
    env: dict[str, str] | None = None,
    verify_assets: bool = True,
) -> DistributionDoctor:
    """Inspect local readiness without network calls or filesystem mutation."""

    values = env or dict(os.environ)
    paths = resolve_paths(cwd=cwd, env=values)
    capabilities: list[CapabilityDiagnostic] = []
    if _writable(paths.state_root):
        capabilities.append(
            CapabilityDiagnostic(
                capability="user-state",
                state="ready",
                detail="resolved state root is writable or can be created by the user",
                evidence=EvidenceRecord(level="observed", source="filesystem"),
            )
        )
    else:
        capabilities.append(
            CapabilityDiagnostic(
                capability="user-state",
                state="blocked",
                detail=str(paths.state_root),
                field="APIFORGE_HOME",
                unlock="choose a writable user-owned APIFORGE_HOME",
                evidence=EvidenceRecord(level="observed", source="filesystem"),
            )
        )
    for command, capability in (("git", "git-read"), ("apiforge-mcp", "mcp-stdio")):
        executable = shutil.which(command)
        capabilities.append(
            CapabilityDiagnostic(
                capability=capability,
                state="ready" if executable else "unavailable",
                detail=executable or f"{command} is not on PATH",
                field="PATH",
                unlock=f"install or expose {command} only if this optional capability is needed",
                evidence=EvidenceRecord(level="observed", source="PATH"),
            )
        )
    if values.get("APIFORGE_NETWORK", "offline").lower() in {"blocked", "offline"}:
        capabilities.append(
            CapabilityDiagnostic(
                capability="network",
                state="unavailable",
                detail="network is not required for local API Forge operation",
                field="network.mode",
                unlock="enable network only for explicitly requested external adapters",
                evidence=EvidenceRecord(level="declared", source="APIFORGE_NETWORK"),
            )
        )
    else:
        capabilities.append(
            CapabilityDiagnostic(
                capability="network",
                state="unresolved",
                detail="network reachability was not probed",
                field="network.mode",
                unlock="use an external adapter with its own receipt when freshness is needed",
                evidence=EvidenceRecord(level="unknown", source="not-probed"),
            )
        )
    assets = asset_status(verify=verify_assets)
    gaps = tuple(
        f"{item.capability}: {item.detail}" for item in capabilities if item.state != "ready"
    ) + tuple(f"asset {item.asset}: {item.state}" for item in assets if item.state != "present")
    status: Literal["ready", "degraded", "unresolved", "blocked"] = (
        "ready" if not gaps else "degraded"
    )
    if any(item.state == "blocked" for item in capabilities):
        status = "blocked"
    return DistributionDoctor(
        status=status,
        paths=paths.contract(),
        capabilities=tuple(capabilities),
        assets=assets,
        gaps=gaps,
        evidence_level="observed",
    )


def require_writable(path: Path) -> None:
    if not _writable(path):
        raise ContractError(
            "AF-DIST-PATH-INVALID",
            f"{path} is not writable",
        )


__all__ = ["diagnose", "require_writable"]
