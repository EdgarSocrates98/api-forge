"""Evidence-aware capability negotiation across supported agent hosts."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from apiforge.agentops.hosts import HOSTS
from apiforge.contracts.base import ContractError
from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.host import (
    HostCapability,
    HostCapabilityRequest,
    HostDeclaration,
    HostResolution,
)


def default_declarations() -> tuple[HostDeclaration, ...]:
    """Build local declarations from static host layout facts only."""
    declarations: list[HostDeclaration] = []
    for host in HOSTS:
        capabilities = (
            HostCapability(
                capability="subagents",
                state="supported" if host.supports_subagents else "unsupported",
                limits=() if host.supports_subagents else ("host does not expose subagents",),
                evidence=EvidenceRecord(level="declared", source="host-layout"),
            ),
            HostCapability(
                capability="mcp",
                state="supported" if host.supports_mcp else "unsupported",
                limits=() if host.supports_mcp else ("host does not expose MCP",),
                evidence=EvidenceRecord(level="declared", source="host-layout"),
            ),
        )
        declarations.append(
            HostDeclaration(
                host=host.name,  # type: ignore[arg-type]
                adapter_version="static-layout-v1",
                capabilities=capabilities,
                evidence=EvidenceRecord(level="declared", source="apiforge.agentops.hosts"),
            )
        )
    return tuple(declarations)


def negotiate(
    request: HostCapabilityRequest,
    declarations: Iterable[HostDeclaration],
) -> HostResolution:
    """Return the eligible intersection; unsupported hosts stay visible."""
    declaration_map = {declaration.host: declaration for declaration in declarations}
    eligible: list[str] = []
    excluded: list[str] = []
    limitations: list[str] = []
    evidence = []
    for host in request.hosts:
        declaration = declaration_map.get(host)
        capability = (
            next(
                (
                    item
                    for item in declaration.capabilities
                    if item.capability == request.capability
                ),
                None,
            )
            if declaration
            else None
        )
        if declaration is None:
            excluded.append(host)
            limitations.append(f"{host}: no declaration")
            continue
        evidence.append(declaration.evidence)
        if capability is None or capability.state != "supported":
            excluded.append(host)
            limitations.extend(
                f"{host}: {item}"
                for item in (capability.limits if capability else ("capability not declared",))
            )
            continue
        missing = sorted(set(request.required_prerequisites) - set(capability.prerequisites))
        if missing:
            excluded.append(host)
            limitations.append(f"{host}: missing prerequisites {', '.join(missing)}")
            continue
        eligible.append(host)
    return HostResolution(
        capability=request.capability,
        eligible_hosts=tuple(sorted(eligible)),  # type: ignore[arg-type]
        excluded_hosts=tuple(sorted(excluded)),  # type: ignore[arg-type]
        limitations=tuple(sorted(set(limitations))),
        evidence=tuple(evidence),
        next_action="continue" if eligible else "declare or configure a compatible host",
    )


def load_declarations(root: Path) -> tuple[HostDeclaration, ...]:
    """Load optional host-owned JSON declarations without contacting hosts."""
    directory = Path(root) / ".apiforge" / "hosts"
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    if not files:
        return default_declarations()
    declarations: list[HostDeclaration] = []
    for path in files:
        try:
            declarations.append(
                HostDeclaration.model_validate(json.loads(path.read_text(encoding="utf-8")))
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise ContractError(
                "AF-HOST-DECLARATION", f"invalid declaration {path}: {exc}"
            ) from exc
    return tuple(declarations)


def negotiate_from_root(root: Path, request: HostCapabilityRequest) -> HostResolution:
    return negotiate(request, load_declarations(root))
