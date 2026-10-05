"""Compact MCP surface (§88–90): six gateways, the whole capability behind them.

The compact surface never hides capability: ``apiforge_discover`` ranks every
full tool against a query and ``apiforge_call`` dispatches to any of them by
name. Gateway results are pruned (null/empty removed) — the same lossless
rule as ``--output compact``.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.output.render import prune
from apiforge.trust.tools import authorize, load_tool_risk

_TOKEN = re.compile(r"[a-z0-9]+")


def full_tools() -> dict[str, Callable[..., Any]]:
    from apiforge.mcp.tools import GRPC_TOOLS, MIGRATION_TOOLS, OBSERVABILITY_TOOLS, TOOLS

    return {fn.__name__: fn for fn in (*TOOLS, *OBSERVABILITY_TOOLS, *GRPC_TOOLS, *MIGRATION_TOOLS)}


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower().replace("_", " ")))


def _authorize_gateway(tool: str, subject: str = "mcp-gateway") -> None:
    profiles, permissions = load_tool_risk()
    decision = authorize(subject, tool, profiles=profiles, permissions=permissions)
    if decision.decision != "allow":
        raise _refusal(
            decision.code or "AF-TOOL-AUTHZ-DENIED",
            decision.reason,
            decision.field or "tool",
            decision.unlock or "declare an explicit gateway permission",
        )


def apiforge_discover(query: str, limit: int = 8) -> dict[str, Any]:
    """Find the full API Forge tools for a need, e.g. 'grpc breaking' or 'context capsule'."""
    _authorize_gateway("apiforge_discover")
    wanted = _tokens(query)
    ranked = []
    for name, fn in full_tools().items():
        doc = inspect.getdoc(fn) or ""
        name_tokens = _tokens(name)
        score = 2 * len(wanted & name_tokens) + len(wanted & _tokens(doc))
        if score:
            ranked.append((-score, name, doc.splitlines()[0] if doc else ""))
    ranked.sort()
    result: dict[str, Any] = prune(
        {
            "query": query,
            "matches": [
                {"tool": name, "summary": summary, "score": -score}
                for score, name, summary in ranked[: max(1, limit)]
            ],
            "hint": "call a match with apiforge_call(tool, arguments)",
        }
    )
    return result


def apiforge_call(
    tool: str,
    arguments: dict[str, Any] | None = None,
    subject: str = "mcp-gateway",
) -> Any:
    """Run any full API Forge tool by name; use apiforge_discover to find it."""
    _authorize_gateway("apiforge_call", subject)
    tools = full_tools()
    fn = tools.get(tool)
    if fn is None:
        raise _refusal(
            "AF-MCP-TOOL-UNKNOWN",
            f"no tool {tool!r}",
            "tool",
            "run apiforge_discover(query) and pass one of its tool names",
        )
    profiles, permissions = load_tool_risk()
    target_decision = authorize(
        subject,
        tool,
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=tools.keys(),
    )
    if target_decision.decision != "allow":
        raise _refusal(
            target_decision.code or "AF-TOOL-AUTHZ-DENIED",
            target_decision.reason,
            target_decision.field or "target",
            target_decision.unlock or "declare an explicit target grant",
        )
    try:
        inspect.signature(fn).bind(**(arguments or {}))
    except TypeError as exc:
        raise _refusal(
            "AF-MCP-TOOL-ARGS",
            f"{tool}: {exc}",
            "arguments",
            "pass keyword arguments matching the tool signature",
        ) from exc
    return prune(fn(**(arguments or {})))


def apiforge_context(
    target: str | None = None,
    changed: list[str] | None = None,
    base: str | None = None,
    head: str | None = None,
    root: str = ".",
    budget_bytes: int = 16000,
) -> dict[str, Any]:
    """Evidence for an operation (target='POST /x') or what a change impacts (changed/base)."""
    _authorize_gateway("apiforge_context")
    from apiforge.mcp import tools

    if target:
        return dict(prune(tools.context_capsule(target, root=root, budget_bytes=budget_bytes)))
    return dict(
        prune(tools.context_delta(base=base, head=head, changed=changed or None, root=root))
    )


def apiforge_expand(uri: str, root: str = ".") -> dict[str, Any]:
    """Expand one ctx:// ref after verifying its sha256."""
    _authorize_gateway("apiforge_expand")
    from apiforge.mcp import tools

    return dict(prune(tools.context_expand(uri, root=root)))


def apiforge_analyze(
    contract: str, project: str, out_dir: str = ".apiforge/case"
) -> dict[str, Any]:
    """Run the deterministic analysis and persist a case (contract + project)."""
    _authorize_gateway("apiforge_analyze")
    from apiforge.mcp import tools

    return dict(prune(tools.analyze(contract, project, out_dir=out_dir)))


def apiforge_evidence(run_id: str | None = None, root: str = ".") -> dict[str, Any]:
    """Bytes attributed per run and source (tokens stay unresolved without a transcript)."""
    _authorize_gateway("apiforge_evidence")
    from apiforge.mcp import tools

    return dict(prune(tools.economy_stats(root=root, run_id=run_id)))


GATEWAY_TOOLS: tuple[Callable[..., Any], ...] = (
    apiforge_discover,
    apiforge_call,
    apiforge_context,
    apiforge_expand,
    apiforge_analyze,
    apiforge_evidence,
)

__all__ = ["GATEWAY_TOOLS", "apiforge_call", "apiforge_discover", "full_tools"]
