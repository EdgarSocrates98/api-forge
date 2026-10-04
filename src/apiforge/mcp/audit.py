"""§40 tool-surface audit: measured findings over the declared tool set.

Checks implemented, each with a declared threshold from
``rules/tool_surface.yaml``:

- ``oversized_schema`` — argument schema bytes above the limit (observed);
- ``poor_description`` — docstring absent or below the byte floor (observed);
- ``unbounded_list`` — collection-returning docstring without a limit-style
  parameter (hypothesis — the signature cannot prove output size);
- ``overlapping`` — name-token Jaccard at or above the declared ratio
  (hypothesis — names overlap, bodies may differ);
- ``oversized_output`` — only when a benchmark sample measured it (observed);
- ``redundant`` — an exact docstring duplicate under another name (observed).
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.tool_surface import SurfaceFinding, ToolSurfaceAudit
from apiforge.mcp.surface import measure_surface, surface_tools

POLICY_INVALID_CODE = "AF-MCP-SURFACE-POLICY"
POLICY_PATH = Path(__file__).resolve().parents[1] / "rules" / "tool_surface.yaml"


def _load_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or POLICY_PATH
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: {exc}") from exc
    if not isinstance(raw.get("thresholds"), Mapping):
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: thresholds mapping missing")
    accepted = raw.get("accepted") or []
    if not isinstance(accepted, list) or any(
        not isinstance(row, Mapping)
        or not all(isinstance(row.get(key), str) for key in ("tool", "kind", "reason"))
        for row in accepted
    ):
        raise ContractError(
            POLICY_INVALID_CODE,
            f"{policy_path}: accepted must be a list of {{tool, kind, reason}} mappings",
        )
    return dict(raw)


def _tokens(text: str) -> set[str]:
    import re

    return set(re.findall(r"[a-z0-9]+", text.lower().replace("_", " ")))


def _is_unbounded(fn: Any, doc: str, cfg: Mapping[str, Any]) -> bool:
    params = set(inspect.signature(fn).parameters)
    limit_words = set(cfg.get("limit_params") or ("limit", "offset"))
    if params & limit_words:
        return False
    collection_words = set(cfg.get("collection_words") or ("items", "list"))
    return bool(_tokens(doc) & collection_words)


def audit_surface(
    surface: str = "full",
    *,
    benchmark_bytes: Mapping[str, int] | None = None,
    policy: dict[str, Any] | None = None,
) -> ToolSurfaceAudit:
    """Audit the declared surface; findings sorted deterministically.

    ``policy`` accepts the full rules document (``thresholds`` + ``accepted``)
    or a bare thresholds mapping for backward-compatible callers.
    """
    doc_map: Mapping[str, Any] = policy if policy is not None else _load_policy()
    thresholds_raw = doc_map.get("thresholds")
    thresholds: Mapping[str, Any] = (
        thresholds_raw if isinstance(thresholds_raw, Mapping) else doc_map
    )
    accepted_rows: Any = doc_map.get("accepted") or ()
    unresolved: list[str] = []
    findings: list[SurfaceFinding] = []

    measured = measure_surface(surface)
    functions = {fn.__name__: fn for fn in surface_tools(surface)}
    costs = {cost.name: cost for cost in measured.tools}

    schema_cfg = thresholds.get("oversized_schema") or {}
    if isinstance(schema_cfg, Mapping):
        max_bytes = int(schema_cfg.get("max_schema_bytes", 4096))
        for name, cost in sorted(costs.items()):
            if cost.schema_bytes > max_bytes:
                findings.append(
                    SurfaceFinding(
                        kind="oversized_schema",
                        tool=name,
                        evidence="observed",
                        detail=f"schema {cost.schema_bytes}B > {max_bytes}B",
                    )
                )

    doc_cfg = thresholds.get("poor_description") or {}
    min_doc = int(doc_cfg.get("min_doc_bytes", 24)) if isinstance(doc_cfg, Mapping) else 24
    for name, cost in sorted(costs.items()):
        if cost.description_bytes < min_doc:
            findings.append(
                SurfaceFinding(
                    kind="poor_description",
                    tool=name,
                    evidence="observed",
                    detail=f"description {cost.description_bytes}B < {min_doc}B floor",
                )
            )

    # redundant — identical first docstring line under different names.
    docs: dict[str, str] = {}
    for name in sorted(functions):
        docstring = (
            (inspect.getdoc(functions[name]) or "").splitlines()[0].strip()
            if inspect.getdoc(functions[name])
            else ""
        )
        if not docstring:
            continue
        if docstring in docs:
            findings.append(
                SurfaceFinding(
                    kind="redundant",
                    tool=name,
                    evidence="observed",
                    detail=f"identical summary to {docs[docstring]}",
                    refs=(docs[docstring],),
                )
            )
        else:
            docs[docstring] = name

    list_cfg = thresholds.get("unbounded_list") or {}
    for name in sorted(functions):
        if _is_unbounded(
            functions[name],
            inspect.getdoc(functions[name]) or "",
            list_cfg if isinstance(list_cfg, Mapping) else {},
        ):
            findings.append(
                SurfaceFinding(
                    kind="unbounded_list",
                    tool=name,
                    evidence="hypothesis",
                    detail="collection-shaped docstring with no limit-style parameter",
                )
            )

    overlap_cfg = thresholds.get("overlapping") or {}
    ratio = (
        float(overlap_cfg.get("min_shared_tokens", 0.6))
        if isinstance(overlap_cfg, Mapping)
        else 0.6
    )
    names = sorted(functions)
    token_map = {name: _tokens(name) for name in names}
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            left_tokens, right_tokens = token_map[left], token_map[right]
            if not left_tokens or not right_tokens:
                continue
            shared = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
            if shared >= ratio:
                findings.append(
                    SurfaceFinding(
                        kind="overlapping",
                        tool=right,
                        evidence="hypothesis",
                        detail=f"name shares {shared:.0%} tokens with {left}",
                        refs=(left,),
                    )
                )

    if benchmark_bytes is None:
        unresolved.append("oversized_output requires a benchmark sample — run mcp benchmark")
    else:
        output_cfg = thresholds.get("oversized_output") or {}
        max_out = (
            int(output_cfg.get("max_response_bytes", 32768))
            if isinstance(output_cfg, Mapping)
            else 32768
        )
        for name, size in sorted(benchmark_bytes.items()):
            if size > max_out:
                findings.append(
                    SurfaceFinding(
                        kind="oversized_output",
                        tool=name,
                        evidence="observed",
                        detail=f"response {size}B > {max_out}B in benchmark sample",
                    )
                )

    # Declared exceptions: matched hypothesis findings move to `accepted`
    # with their reason — recorded, never silently suppressed.
    accepted: list[SurfaceFinding] = []
    kept: list[SurfaceFinding] = []
    for finding in findings:
        match = next(
            (
                row
                for row in accepted_rows
                if isinstance(row, Mapping)
                and row.get("tool") == finding.tool
                and row.get("kind") == finding.kind
            ),
            None,
        )
        if match is None:
            kept.append(finding)
        else:
            accepted.append(
                finding.model_copy(
                    update={"detail": f"{finding.detail} — accepted: {match.get('reason')}"}
                )
            )
    findings = kept

    findings.sort(key=lambda f: (f.kind, f.tool, f.detail))
    return ToolSurfaceAudit(
        surface=surface,  # type: ignore[arg-type]
        tool_count=measured.tool_count,
        total_bytes=measured.total_bytes,
        findings=tuple(findings),
        accepted=tuple(accepted),
        unresolved=tuple(unresolved),
    )


__all__ = ["audit_surface"]
